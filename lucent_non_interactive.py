#!/bin/env python3

class LucentNonInteractive():

    # Initialize Class.
    def __init__(self):

        import management  # For user and configuration management.
        import sys  # For quitting script.
        import sql_interop as si  # For interacting with database.

        # Load configuration.
        try:
            # Use first element, because loadDictianories returns list
            # of dictianories.
            self.config = management.loadConf("./conf/config.yaml")
        except FileNotFoundError:
            print(_("Configuration file(s) not fould. Aborting …"))
            sys.exit(1)  # Abort execution.
        except Exception as e:
            print(f"Error while loading configuration. Aborting … \n{e}")
            sys.exit(1)  # Abort execution.

        # Get user who initially called the script, maybe via sudo or doas …
        try:
            self.user = management.getSudoingUser()
        except Exception as e:
            print(f"Couldn't get user, {e}. Aborting …")
            sys.exit(1)

        # Establish database connection.
        try:
            self.sqlConnection = si.databaseConnection(self.config)
        except Exception as e:
            print(f"Couldn't establish database connection, {e}.")

    # Dummy method.
    def aboutMe(self):
        print(f"User: {self.user} \nSQL connection: {self.sqlConnection}")
        print(self.config)
