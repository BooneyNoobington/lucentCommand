# Compile a list of options to present to the user.
def getOptions(sqlConnection, tableOrView, where = "", viewAllowed = True):

    import sql_interop as si  # Talk to the database.
    import mariadb  # Handle sql related errors.

    # Compile a list of dictianories which represent the options.
    if viewAllowed:
        # Views which provide readable choosing info are usually prefixed with "attach".
        try:
            options = si.fetchData(
                sqlConnection, f"SELECT * FROM `attach_{tableOrView}` {where};"
            )
        # If the view doesn't exist, interpret argument as simple table.
        except mariadb.ProgrammingError:
            options = si.fetchData(sqlConnection, f"SELECT * FROM `{tableOrView}` {where};")
        # Catch other stuff that might go wrong.
        except Exception as e:
            print(f"Error retrieving options for picker, {e}.")
            return {}  # Return an empty list. Anything that calls getOptions will have cope.
    else:  # No views are allowed.
        options = si.fetchData(sqlConnection, f"SELECT * FROM `{tableOrView}` {where};")

    return options
