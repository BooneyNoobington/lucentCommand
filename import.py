#/bin/env python3


# Function to determine id of dataset in joined table.
def getForeignKey(
    dictianory
  , joinedTableName
  , stringIdentifier = "name"
  , sqliteConnection = None
  , verbose = False
):

  import sqlite_interop as si  # For the

  # Check wether the passed dictianory has a key called "id"
  # for the joined table in question.
  try:
    subspotId = s[joinedTableName]["id"]
  # If this operation fails, id was provided for the import
  except KeyError:
    if verbose: print("No id key found, try looking up by name.")

    # Contingency: Try to look up the id by referencing the name.
    try:
      subspotName = s[joinedTableName][stringIdentifier]
    except Exception as e:
      print("Name key also not found. Aborting...")

    try:
      subspotId = si.fetchData(
          sqliteConnection
        , "SELECT ID_SUBSPOT FROM `" + joinedTableName + "` WHERE" + stringIdentifier + "= \'" + subspotName + "\'"
      )[0]["id_subspot"]
    except NoneType:
      print("Was a connection to a SQLite database provided?")
      exit(1)
    except Exception as e:
      print(e)
      exit(1)

    return subspotId
