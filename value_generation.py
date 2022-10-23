#!/bin/env python3

# These functions describe ways to get / compute values which
# aren't known at the time a employee puts together their yaml files.
# No error handling. Calling function needs to take care of that.

# Look up a value by a parsed sql query.
def generateBySQL(sqlConnection, query, k, fl, vl, verbose = False):

    import sql_interop as si  # Database connection.
    import inspect  # For reflection.

    print(f"Pulling information for {k} from sql query {query}")

    # Retreive the value by provided sql query.
    resultList = si.fetchData(sqlConnection, query)

    # Add to lists by reference.
    try:
        retrievedValue = resultList[0][k]
    except Exception as e:
        print(f"Got a result but could not retreive value. {e}")
        print(resultList)

    print(f"SQL query retrieved {retrievedValue} for {k}.")

    # Append the new found key and value to respective lists.
    fl.append(k)
    vl.append(retrievedValue)


# Automatically generate a value.
# Retrieve the primary key. It is to be incremented.
def autoGenerate(sqlConnection, tableName, k, fl, vl, computation, verbose = False):

    import sql_interop as si  # For looking up the primary key.
    import numbering as n  # For incrementation functions.

    # Retrieve the primary key for a specific table.
    primaryKey = si.getPrimaryKey(sqlConnection, tableName)

    if verbose:
        print(
            f"Automaticalle generating value for {primaryKey} in {tableName}."
        )

    # Try to get new maximum.
    try:
        oldMax = si.fetchData(
              sqlConnection
              # Build the query string simply by using variables about
              # the pk and table.
            , f"SELECT MAX({primaryKey}) AS OLD_MAX FROM `{tableName}`"
        )[0]["OLD_MAX"]
        # Append the key.
        fl.append(k)
        # Calculate and append the new maximum number.
        newMax = n.getNextNumber(oldMax, computation)
        vl.append(newMax)

        print(
            f"Auto generated primary key value {newMax} for table {tableName}"
        )

    except Exception as e:
        print(f"Error while auto generating id. {e}")
