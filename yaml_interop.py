#!/bin/env python3

### Turn yaml info into dicatianories ###
def loadDictianories(filename, toDict = True):

    import yaml  # Basic yaml handling.

    # Error handling by calling function.
    try:
        stream = open(filename, "r")
    except FileNotFoundError:
        print(f"YAML file {filename} doesn't exist, {e}.")
        return -1

    # Convert the yaml info to a dicatianory.
    try:
        dictianories = yaml.load_all(stream, yaml.FullLoader)
    except Exception as e:
        print(e)

    # By default turn the data into actual dictianories.
    return list(dictianories) if toDict else dicatianories

