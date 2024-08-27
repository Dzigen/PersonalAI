import os
import json

class Logger:
    def __init__(self, path):
        self.path = path
        os.makedirs(path, exist_ok=True)
        
    def __call__(self, text, filename = "log.txt", verbose = True):
        if verbose:
            print(text)
        with open(self.path + "/" + filename, "a") as file:
            file.write(text + "\n")
            
    def to_json(self, obj, filename = "history.json"):
        try:
            with open(self.path + "/" + filename, "w") as file:
                json.dump(obj, file)
        except:
            raise "Object isn't json serializible"