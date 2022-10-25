# Helper function for genericImportDictionaries.
# Add keys and values that need to be looked up to their respective list.

def completeKeysAndValuesList(
    caller
  , dictianory
  , fl
  , vl
  , knownPrimaryKeys
  , verbose = False
):

    import sql_interop as si  # For database queries.
    import inspect  # For relection.
    import value_generation as vg  # For individual functions.

    # Extract list with fields and values dictianories from main dic.
    try:
        fav = dictianory["fields and values"]
    except KeyError:
        print("No key \'fields and values\' in fav! Aborting …")
        exit(1)

    # Handle the values that have to be looked up.
    # Loop over all dictianories in the list fields and values.
    for d in fav:
        # Loop over their keys and values.
        for k, v in d.items():
            # If a d is encountered the value has to be looked up.
            if type(v) is dict:
                try:
                    # Case: A value is to be supplied by an sql query.
                    if d[k]["get by"] == "sql":
                        vg.generateBySQL(
                            caller.sqlConnection
                          , d[k]["query"]
                          , k, fl, vl
                          , verbose
                        )

                    # Case: A value should be automatically generated.
                    # Like a running number

                    elif d[k]["get by"] == "auto generate":

                        # If no type is defined, use "running".
                        try:
                            computationType = d[k]["type"]
                        except KeyError:
                            computationType = "running"

                        vg.autoGenerate(
                            caller.sqlConnection
                          , dictianory["table name"]
                          , k, fl, vl
                          , computationType
                          , verbose
                        )

                    # If a new primary key was already calcuated for another
                    # table and should now be used in another one.
                    # Useful for n to m relations.
                    elif d[k]["get by"] == "generated primary key":

                        # Add the disered primary key to the field list.
                        fl.append(k)

                        # Retrieve the known primary key from table.
                        try:
                            pkv = knownPrimaryKeys[d[k]["table name"]]
                            # Add the retrieved primary key value into the
                            # value list.
                            vl.append(pkv)
                        except KeyError:
                            print(f"No primary key known.")
                            return -1

                        print(f"Using {pkv} as id for {k}")

                except KeyError:
                    pass
                except Exception as e:
                    print(
                        f"An error happend in: completeKeysAndValuesList \n {e}"
                    )



# Generic import function.
def genericImportDictionaries(
    caller
  , dictianories
  , primaryKeys = {}  # Keep track of known primary keys and their values.
  , verbose = False
):

    import yaml_interop as yi  # For loading additional files.
    import sql_interop as si  # For querying and manipulating database.
    import helpers as h  # Various helper functions.
    import more_itertools as mi  # For flattening a list.
    import sys  # Abort execution.

    # First: Extract the datasets which have to be created beforehand.
    yamlFiles = [d["before"] for d in dictianories if "before" in d.keys()]

    # This list as to be "flattend" since it's in a form like
    # [[1, 2], [3, 4]]
    if len(yamlFiles) > 0:
        yamlFilesFlat = [
            caller.config["data dir"]["path"]
            + "/generic_registration/" + x for x in mi.flatten(yamlFiles)
        ]

        # Remove dupes.
        yamlFilesFlatNoDupes = list(set(yamlFilesFlat))

        print("These files need to be processed beforhand:")
        print(yamlFilesFlatNoDupes)

        # For every file recurse this function.
        try:
            for f in yamlFilesFlatNoDupes:
                print(f"Handling additional insert for: {f}")
                handleBeforehand = yi.loadDictianories(f)

                print("List of known primary keys:")
                print(primaryKeys)

                # Recurse this function.
                genericImportDictionaries(
                    caller = caller
                    , dictianories = handleBeforehand
                    , primaryKeys = primaryKeys
                    , verbose = verbose
                )
        except FileNotFoundError:
            print(f"File {f} not found. Aborting …")
            return -1  # Abort executiion.

    # Loop over all documents in the parsed yaml file.
    for document in dictianories:
        fav = document["fields and values"]

        # Extract the name of the table in question.
        try:
            handlingTable = document["table name"]
        except KeyError:
            print("Name of the table in question not found.")
            sys.exit(1)


        print(f'Trying import for: {handlingTable}')

        # Get fields that can be inserted directly
        listFields = [k for f in fav for k, v in f.items() if type(v) is not dict]
        listValues = [v for f in fav for k, v in f.items() if type(v) is not dict]

        # Call helper function.
        completeKeysAndValuesList(
              caller
            , document
            , listFields
            , listValues
            , primaryKeys
            , verbose
        )

        # Execute the insert for the main table.
        try:
            pk, pkv = si.genericInsert(
                caller.sqlConnection
                , handlingTable
                , listFields
                , [str(v) for v in listValues]  # Transform into string.
                , verbose
            )
        except ValueError:
            print("List of fields and List of values are of differnt length.")
            print(listFields)
            print(listValues)
        except Exception as e:
            print(f"genericInsert producede: {e}")

        # Keep track of known primary keys and their values.
        primaryKeys[handlingTable] = pkv


# Manually insert a record.
def registerManually(caller, table):

    import sql_interop as si  # For interaction with the database.
    import mariadb  # For cataching mariadb related erorrs.
    import pick  # Choose an option.
    import numbering as n  # For setting primary keys.

    # Get all fields of the table in question.
    tableCols = si.fetchData(
        caller.sqlConnection
      , f"SHOW COLUMNS FROM `{table}`;"
    )

    # Reduce to "Field" column.
    tableFields = [d["Field"] for d in tableCols]

    # Get all the references to other tables.
    tableRefs = si.fetchData(
        caller.sqlConnection
      , si.buildQueryString(
            "./sql/GET_TABLE_REFS.SQL"
          , {"table": table}
        )
    )

    # Get primary key and current max.
    primaryKey = si.getPrimaryKey(caller.sqlConnection, table)
    currentMax = si.fetchData(
        caller.sqlConnection, f"SELECT MAX({primaryKey}) AS mid FROM `{table}`"
    )
    try:
        newMax = n.getNextNumber(currentMax[0]["mid"])
    except Exception as e:
        print(f"Error generating value for {primaryKey}, {e}")
        return -1

    # Set the fields and values lists for generic insert.
    # Right now they only contain pk and its value. Later other info will be appended.
    fieldList = [primaryKey]
    valueList = [newMax]

    # Extract only fields from entire dictianories.
    tableRefFields = [e["referencingCol"] for e in tableRefs]

    # Get all non refs.
    nonRefs = [e for e in tableFields if e not in tableRefFields]

    # Remove primary key.
    nonRefs.pop(nonRefs.index(primaryKey))

    # Fill out all the columns which don't reference another table.
    for l in nonRefs:

        # Ask the user.
        try:
            value = input(f"Please input a value for {l}: ")
        except Exception as e:
            print(f"Error reading value, {e}.")

        # Append to keys and values list.
        fieldList.append(l)
        valueList.append(value)

    # Fill out all table references.
    for ref in tableRefs:

        # Get variables from query result.
        try:
            refToTable = ref["refToTable"]
            referencingCol = ref["referencingCol"]
            refToColumn = ref["refToColumn"]
        except KeyError:
            print("Error: Important field could not be retriefed.")
            return -1
        except Exception as e:
            print(f"Error: Undefined error when collecting table references, {e}")
            return -1

        # Obtain nice list by predefined view.
        try:
            options = si.fetchData(
                caller.sqlConnection
              , f"SELECT * FROM `attach_{refToTable}`;"
            )
        # Otherwise fall back to referenced table itself.
        except mariadb.ProgrammingError:
            options = si.fetchData(
                caller.sqlConnection
              , f"SELECT * FROM `{refToTable}`;"
            )
        # Catch random errors.
        except Exception as e:
            print(f"Error getting options for {refToColumn}, {e}.")
            return -1

        # Turn options to string for nicer output.
        optionsStr = [str(d).replace("{","").replace("}","").replace("\'","") for d in options]

        # Have the user choose.
        try:
            picked, index = pick.pick(optionsStr, f"Select a value for {referencingCol}:")
        except Exception as e:
            print(
                f"You are trying to insert a record into {table}. \n" +
                f"But there are no choices for {referencingCol}. \n" +
                f"Please provide a fitting dataset in {refToTable}."
            )
            return -1

        # Append the information.
        fieldList.append(ref["referencingCol"])
        # TODO: Does this mean, that the referencing / referenced column has to have the same name
        # in both tables? Won't work all the time... Maybe replace column name dynamically.
        valueList.append(options[index][ref["referencingCol"]])

    # Execute the insert.
    # Stringify values for generic insert.
    si.genericInsert(caller.sqlConnection, table, fieldList, valueList)
