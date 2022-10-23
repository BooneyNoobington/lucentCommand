#!/bin/env python3
import cmd  # The interactive shell.

# Localisation.
import gettext
_ = gettext.gettext


# Actual terminal.
class lucentTerminal(cmd.Cmd):

    # Initzalize this object.
    def __init__(self):

        # Imports.
        import sys  # Mainly for ending the programm after a critical error.

        # Get the locale.
        import locale  # Itendifying the locale.
        # Get information about the environment.
        currentLocale = locale.getlocale()[0]  # The second index is the encoding.

        # Initialize the command line.
        cmd.Cmd.__init__(self)

        # Setup prompt and user info.
        import management  # For loading configuraiton and determine user.
        self.user = management.getSudoingUser()
        self.prompt = self.user + "@" + "lucentLIMS>> "
        self.intro = "\nlucentLIMS 0.0.1, Locale: " + currentLocale

        # Load configuration.
        import yaml_interop as yi  # Open yaml files.

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

        # Setup a history file for the user logged in.
        # Can't place it in home directory. No write access.

        # Set up info regarding history file.
        histfile_size = 1000  # Remember the last one thousand inputs.

        try:
            histDir = self.config["data dir"]["path"] + f"/command_history/{self.user}"

            # Make sure that this directory exists.
            import pathlib  # For ensuring the existence of a directory.
            pathlib.Path(histDir).mkdir(parents = True, exist_ok = True)

            # Set the hist file.
            self.histFile = histDir + "/lucent_history"
        except Exception as e:
            print(f"Error: Couldn't create command history file, {e}.")

        # Database connection is essential.
        import sql_interop as si

        try:
            self.sqlConnection = si.databaseConnection(self.config)
        except Exception as e:
            print(f"Error while loading database, {e}.")
            sys.exit(1)


        # Initialize logging settings.
        import logging  # For well formatted log output.
        import datetime  # Date and time operations.

        try:
            # Get the current day.
            today = datetime.datetime.now().strftime("%Y.%m.%d")

            # Set up the basic logging configuration.
            logging.basicConfig(
                # Logfile ends with current day.
                filename = self.config["logging"]["log dir"] +
                    "/lucentLIMS-" + today + ".log"
                # Format and level from configuration file.
              , format = self.config["logging"]["format"]
              , level = self.config["logging"]["log level"]
            )

            # Initialize a logger. Keep the name simply: Path of the
            # calling script.
            lucentLogger = logging.getLogger(__file__)

        except Exception as e:
            print(f"Logging Initialization failed, {e}. Quitting…")
            sys.exit(1)  # This 100% has to work. Otherwise quit.


        # Print a warning if logs would be incomplete.
        if self.config["logging"]["log level"] > 20:
            print(_("Logs won't include info messages. This system can't be usef for production."))

        # Give an information about the start of these app.
        lucentLogger.info(_(f"lucentLIMS has initialized as {self.user}."))




    ### Actions to run before command line appears ###

    # If a command line history file exists, load it.
    def preloop(self):
        import os  # Check wether path exists.
        import readline  # Load a command history.

        if os.path.exists(self.histFile):
            readline.read_history_file(self.histFile)




    ### Actions to run after the command line closes ###

    # Create / update the history file.
    def postloop(self):
        import readline  # Save the command history.
        readline.set_history_length(histfile_size)
        readline.write_history_file(self.histFile)




    ### Methods of this object ###
    import lucent_functions

    # Registering datasets.
    def do_register(self, line):
        import lucent_functions
        # Pass the entire line. Too complex to be handled by cliFromStr.
        lucent_functions.registerRecord(self, line)


    # Attaching n to m relations.
    def do_attach(self, line):

        import lucent_functions

        # Process the given command line.
        l = lucent_functions.cliFromStr(line, ["command"])

        if l["command"].lower() == "analysis" or l["command"].lower() == "analyses":

            import nm_attach as na

            na.attachAnalysis(self)




    ### Miscellaneous methods ###

    # Print some basic sample information.
    def do_query(self, line):
        import lucent_functions
        lucent_functions.simpleQuery(self)

    # Send a message to another user.
    def do_message(self, line):
        import lucent_functions
        lucent_functions.sendMessage(self, line)

    def do_config(self, line):
        import pprint
        pprint.pprint(self.config)

    def do_use(self, line):
        l = lucent_functions.cliFromStr(line, ["command"])

        # Select a specific sample. Can be used for simplifying other actions.
        if l["command"].lower() == "sample":

            # Imports.
            import sql_helpers as sh  # Small sql related functions.
            import pick  # Choose an options from a list.

            # Options are all samples.
            options = sh.getOptions(self.sqlConnection, "sample")

            # Execute the picking.
            sample, index = pick.pick(options, _("Please choose a sample to attach analyses to."))

            # Select by id.
            try:
                sampleId = sample["id_sample"]
            except Exception as e:
                print(f"Error choosing a sample, {e}.")
                return -1

            # Safe the selected sample as attribute of the terminam.
            self.use = "sample"
            self.useId = sampleId

            # Change prompt.
            self.prompt = self.user + "@" + "lucentLIMS[sample ID: " + str(sampleId) + "]>> "


    def do_info(self, line):

        import sql_interop as si
        import helpers as h
        import mariadb

        try:
            primaryKey = si.getPrimaryKey(self.sqlConnection, self.use)

            try:
                infoList = si.fetchData(
                    self.sqlConnection
                  , f"SELECT * FROM `attach_{self.use}` WHERE {primaryKey} = {self.useId}"
                )
            except mariadb.ProgrammingError:
                infoList = si.fetchData(
                    self.sqlConnection
                  , f"SELECT * FROM `{self.use}` WHERE {primaryKey} = {self.useId}"
                )
            print(h.dictianoriesToTable(infoList))
        except AttributeError:
            print("Currently no record in use.")



    ### Functions regarding the user ###
    def do_my(self, line):

        import shlex  # For splitting strings respecting whitespace escapes.

        # Turn command line into seperate arguments.
        lineAsList = shlex.split(line)

        # Multiple subcommands are possible.
        try:
            if lineAsList[0] == "messages":
                lucent_functions.getMessages(self)
        except IndexError:
            print("No subcommand for command \'my\' provided.")




    # TODO: Autocompleten by: complete_<function name>

    def do_EOF(self, line):
        return True


# Execute main function.
if __name__ == '__main__':
    lucentTerminal().cmdloop()
