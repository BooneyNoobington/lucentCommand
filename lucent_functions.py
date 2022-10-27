# All of these functions are meant to be executed from an obect "caller"
# and passed a list of arguments "commandLine."

# Localisation.
import gettext
_ = gettext.gettext




# For a command line from a string.
def cliFromStr(line, argumentsList):

    import shlex  # For string splitting respecting whitespace escapes.
    lineAsList = shlex.split(line)  # Tear the string apart.

    # Initialize empty dictianory for arguments and their values.
    argsAndVals = {}

    # Sanity check.
    if len(argumentsList) != len(lineAsList):
        print("Can't interpret command line. Two few or much arguments provided.")

    # Assign every argument its value.
    try:
        i = 0  # TODO: More pythonic way?
        # Loop over all passed argument names.
        for arg in argumentsList:
            # Assign value.
            argsAndVals[arg] = lineAsList[i]
            # Increment counter.
            i = i + 1
    except Exception as e:
        print(f"Error interpreting command line, {e}.")
        return -1

    return argsAndVals




# Register a record. Either generically or by calling another
# custom function from directory "registration routines".
def registerRecord(caller, commandLine):

    # Imports.
    import yaml_interop as yi
    import register as r
    import helpers as h
    # Look for possible predefined python files.
    import os.path  # Check wether file exists.
    import sys  # Add subfolders to possible import paths.
    import importlib  # Load modules dynamically.
    import inspect

    # Convert command line to a list.
    lineAsList = commandLine.split()

    # When looking for importable files also look here.
    sys.path.insert(1, "./registration_routines/")

    # Possible module.
    module = lineAsList[0]
    modulePath = "./registration_routines/" + lineAsList[0] + ".py"

    # Check wether such a file exists.
    if os.path.exists(modulePath):

        # Try to import the predefined import routine as module.
        try:
            custom_reg_routine = importlib.import_module(lineAsList[0])
        except Exception as e:
            print(myMessages["general import error"].format(module = module))
            print(e)

        # Execute the function "customRegister(…)"
        # from the module just loaded.

        # Transform a list to a mapping.
        try:
            kwargs = dict(arg.split('=') for arg in lineAsList[1:])
        except ValueError:
            print(myMessages["kav usage"])

        # Call Function with arguments provided by argumentsMapping.
        try:
            print(
                myMessages["executing custom routine"].format(
                    module = module, arguments = " ".join(lineAsList)
                )
            )
            custom_reg_routine.customRegister(**kwargs)
        except Exception as e:
            print(myMessages["general execution error"])
            print(e)

    # Generic import functionality. YAML files need to be generically
    # formatted.
    elif lineAsList[0].lower() == "generic":

      # Interpret the command line.
      try:
          yamlFile = caller.config["data dir"]["path"] + "/generic_registration/" + lineAsList[1]
          open(yamlFile)
      except FileNotFoundError:
          print(_(f"YAML file {lineAsList[1]} not found."))
          return -1
      except Exception as e:
          print(_(f"General error in loading file for generic import, {e}."))

      try:
          verbose = False if lineAsList[2] is None else h.strToBool(lineAsList[2])
      except IndexError:
          verbose = False  # No verbose if nothing was stated.
      except Exception as e:
          print(_(f"General error in loading file for generic import, {e}."))

      # Call generic import function.
      r.genericImportDictionaries(
          caller
        , yi.loadDictianories(yamlFile)
        , verbose = False
      )

    # Manually register record.
    elif lineAsList[0].lower() == "manual":
        try:
            r.registerManually(caller, lineAsList[1])
        except IndexError:
            print("Please provide table name.")
            return -1
        except Exception as e:
            print(f"Other error trying to manually register record, {e}")
            return -1


    else:
        print(myMessages["no routine"].format(routine = module))




# Function to execute a pre defined or simple query.
def simpleQuery(caller):

    import helpers as h  # Small helper functions.
    import sql_interop as si  # Interactivity with database.
    import os  # Operating system related methods.
    import pick  # Have the user pick an option.

    # The list command can take a prepared query file.
    try:

        queryDir = caller.config["data dir"]["path"] + "/custom_queries"

        # Use pick to let the user choose a file.
        queryFile, index = pick.pick(
            # Return format of pick is a little strange. Gives list of
            # tuples and other lists.
            [f for f in os.walk(queryDir)][0][2]
          , _("Please pick a custom query.")
        )

        # Just execute the query.
        listInfo = si.fetchData(
            caller.sqlConnection
          , si.buildQueryString(queryDir + "/" + queryFile)
        )

    # Handle exceptions.
    except IndexError:  # Happens if file the path that's walked doesn't exist.
        print(_(f"The directory {queryDir} doesn't exist."))

        # Quit function here, otherwise UnboundVariableError.
        return -1

    except ValueError:  # Emtpy list.
        print("No files to display here.")
        return -1  # Same as above.

    except Exception as e:
        print(_(f"Error while executing {queryFile}, {e}."))
        print(queryFile)

    # Tranform dictianories into a readable table.
    try:
        print(h.dictianoriesToTable(listInfo))
    except IndexError:
        print("No data.")




# Function to send a message to another lucent user.
def sendMessage(caller, commandLine):

    import shlex  # For splitting strings respecting whitespace escapes.

    # Turn command line into seperate arguments.
    lineAsList = shlex.split(commandLine)

    # Extract variables from command line.
    try:
        reciever = lineAsList[0]
        subject = lineAsList[1]
        message = lineAsList[2]
    except IndexError:
        print("Please supply reciever, subject and message.")
        return -1
    except Exception as e:
        print(f"Error parsing command line arguments. {e}")
        return -1

    # Determine wether the reciever exists.
    import sql_interop as si

    resultList = si.fetchData(
        caller.sqlConnection
      , si.buildQueryString("./sql/GET_PERSON.SQL", {"reciever": reciever})
    )

    # Try to extract the unix account from the result set.
    try:
        recieverUnixAccount = resultList[0]["unix_account"]
    except Exception as e:
        print(f"No unix account for {reciever} could be found. {e}")
        return -1

    # User feedback.
    print(
        f"Sending message \"{message}\" with subject " +
        f"\"{subject}\" to {recieverUnixAccount}"
    )

    # Insert message into database.

    # TODO: If every rdms can auto incement, this is really unneccesary.
    # Get the highest message id.
    messagePK = si.getPrimaryKey(caller.sqlConnection, "message")

    latestIdMessage = si.fetchData(
        caller.sqlConnection
      , f"SELECT MAX({messagePK}) AS mid FROM `message`"
    )[0]["mid"]

    # Ececute insert.
    si.genericInsert(
        caller.sqlConnection
      , "message"
      , ["id_message", "sender", "reciever", "subject", "message"]
        # Stringify for generic insert
      , [str(x) for x in
            # Build list of values.
            [
                  latestIdMessage + 1 if not latestIdMessage is None else 1
                , caller.user
                , recieverUnixAccount
                , subject
                , message
            ]
        ]
    )



# Function to display all messages of current user.
def getMessages(caller):

    import pick  # For listing and selecting the messages.
    import sql_interop as si  # For database quieries.
    import helpers as h  # To turn string into boolean.

    # Collect messages.
    myMessages = si.fetchData(
        caller.sqlConnection
      , f"SELECT * FROM `message` WHERE reciever = '{caller.user}' AND read_status = 0"
    )

    # Display picker.
    try:
        subject, index = pick.pick(
            [s["subject"] for s in myMessages]  # Queries result in dictianories.
          , f"Messages for {caller.user}"
        )
    except ValueError:
        print(f"No unread messages for {caller.user}")
        return -1

    # Display message.
    print("\n" + subject + "\n" + myMessages[index]["message"] + "\n")

    # Ask if this message is to be marked as read.
    readOrNot = h.strToBool(input("Mark this message as read? [y|n] "))

    # Use this statement for marking the message as read.
    if readOrNot:
        messageId = myMessages[index]["id_message"]
        statementRead = f"UPDATE `message` SET read_status = 1 WHERE id_message = {messageId}"

        # Execute statement.
        si.executeStatement(caller.sqlConnection, statementRead)



# Manually initate calculations.
def calc(caller):
    # Make sure a sample is selected for use.
    try:
        usedTable = caller.use
        usedId = caller.useId
    except AttributeError:
        print("Please choose a sample first. \nUsage: use sample")
        return -1

    # Extract a list of options.
    import sql_helpers as sh
    options = sh.getOptions(caller.sqlConnection, "readable_result")

    # Have the user pick one ore more results to calculate.
    import pick
    toCalc = pick.pick(options, multiselect = True)

    # Extract the dictianories from the list of tuples.
    toCalcDicts = [t[0] for t in toCalc]

    # Extract the ids of the results to be calculated.
    toCalcIds = [d["id_result"] for d in toCalcDicts]

    # Loop over all chosen results and initiate calculation.
    import os  # For calling other scripts in the lucent directory.
    for r in toCalcDicts:
        print("Exectuing {calculation}".format(calculation = r["calculation"]))

        # Make sure a calculation is set.
        if r["calculation"] != "NULL":
            # If the file exists, try to execute the calculation script.
            try:
                print(
                    "Executing: {script} {argument}".format(
                        script = r["calculation"]
                      , argument = str(r["id_result"])
                    )
                )
                os.system(r["calculation"] + " " + str(r["id_result"]))  # This should call the script.
            # If the file isn't there inform the user about the problem.
            except FileNotFoundError:
                print(
                    "Error: Calculation script {script} doesn't exist}".format(
                        script = r["calculation"]
                    )
                )

