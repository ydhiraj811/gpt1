import g4f
from flask import Flask, request
from flask_cors import CORS

import importlib
import glob
import os

provider_files = glob.glob(os.path.join('g4f', 'Provider', '*.py'))
provider_modules = [os.path.splitext(os.path.basename(path))[0] for path in provider_files]
skip = ['__init__', 'base_provider', 'helper', 'retry_provider']
for i in skip:
    provider_modules.remove(i)

print(provider_modules)
_providers = []
for module_name in provider_modules:
    module = getattr(importlib.import_module(f"g4f.Provider.{module_name}"), module_name)
    if module.working:
        _providers.append(module)

#https://github.com/xtekky/gpt4free#gpt-35--gpt-4

app = Flask(__name__)
CORS(app)

@app.route('/', methods=['POST', "HEADER", "GET"])
def gpt():
    global _providers
    if request.method=="POST":
        
        if 'messages' in request.json:
            messages = request.json['messages']
        elif 'message' in request.json:
            message = request.json['message']
        else:
            return {"text":"Invalid Request"}, 400
        #working = _providers
        for prod in _providers:
            
            try:
                if 'messages' in request.json:
                    response = g4f.ChatCompletion.create(
                        model="gpt-3.5-turbo",
                        provider=prod,
                        messages=messages,
                        stream=False,
                    )
                else:
                    response = g4f.ChatCompletion.create(
                        model="gpt-3.5-turbo",
                        provider=prod,
                        messages=[{"role": "user", "content": message}],
                        stream=False,
                    )
                print(prod, response)
                break
            except Exception as E:
                print(str(E))
                # working.append(prod)
                # del working[working.index(prod)]
                # print("Moved To Back:", prod)
        return {"text":response}
        
    else:
        return "WORKING!"

if __name__ == "__main__":
    print(_providers)
    app.run(host='0.0.0.0', port=5000, debug=False)
