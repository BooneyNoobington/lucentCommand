#!/bin/env python3

# Get a dictionary form a list of dictianories.
def selectDictianory(lod, key, value):
    # Iterate over all dictianories and pick the right one.

    returnDic = next(
        (dic for dic in lod if dic[key] == value)
      , None
    )

    return returnDic


# Check wether a given string is a valid path.
def ensurePath(string):
    import os

    if os.path.isdir(string):
        return string
    else:
        raise NotADirectoryError(string)





# Transform a string to a true or false boolean.
def strToBool(
    s
  , trueValues  = ["true", "t", "yes", "y", "1"]
  , falseValues = ["false", "f", "no", "n", "0"]
):

  if s.lower() in trueValues:
    return True
  elif s.lower() in falseValues:
    return False
  else:
    return False


# List of dictianories as table.
def dictianoriesToTable(lod):
    import tabulate
    try:
        header = lod[0].keys()
        rows =  [x.values() for x in lod]
        return tabulate.tabulate(rows, header)
    except KeyError:
        print("Key error in translating dictianory to table.")
