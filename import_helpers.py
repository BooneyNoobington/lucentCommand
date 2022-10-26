#/bin/env python3


# Function to determine id of dataset in joined table.
def getForeignKey(
    dictianory
  , joinedTableName
  , stringIdentifier = "name"
  , joinedTableIdField = None
  , sqliteConnection = None
  , verbose = False
):

  import sqlite_interop as si  # For querying the joined table id.

  # If No id field is specified assume generic "id_<table name>".
  if joinedTableIdField == None:
    joinedTableIdField = "id_" + joinedTableName

  # Check wether the passed dictianory has a key called "id"
  # for the joined table in question.
  try:
    joinedTableId = dictianory[joinedTableName]["id"]
  # If this operation fails, id was provided for the import
  except KeyError:
    if verbose: print("No id key found, try looking up by name.")

    # Contingency: Try to look up the id by referencing the name.
    try:
      joinedTableReadableId = dictianory[joinedTableName][stringIdentifier]
    except KeyError:
      print(
          "Could not determine the readable identifier for " + #
            joinedTableName + "\nThis is essential. Aboirting …"
      )
      exit(1)
    except Exception as e:
      if verbose: print("Name key also not found. Aborting...")
      print(e)
      exit(1)

    # Now try to find the id in the respective table.
    try:
      queryResult = si.fetchData(
          sqliteConnection
        , "SELECT " + joinedTableIdField + " FROM `" +
            joinedTableName +
            "` WHERE " + stringIdentifier + " = \'" + joinedTableReadableId + "\'"
      )
      joinedTableId = queryResult[0][joinedTableIdField]
    # What happens if there is no result?
    except IndexError:
      print("Tried looking up \'" + joinedTableReadableId + "\' in \'" + joinedTableName + "\' but got no result. Aborting…")
      exit(1)
    except Exception as e:
      print("While executing a query to find the joined table id an error occured.")
      print(e)
      exit(1)

    return joinedTableId
