# Attach n to m relations to records.

# Localisation.
import gettext
_ = gettext.gettext

# Attach an analysis to sample.
def attachAnalysis(caller):

    import pick  # Pick a sample.
    import sql_interop as si  # Interact with database.
    import sql_helpers as sh  # Small sql functions.
    import numbering as n  # Get a new running number for a result.

    # Select a sample.
    try:
        if caller.use == "sample":
            sampleId = caller.useId  # Maybe there is already one selected.
    # If not have the user pick one.
    except AttributeError:
        optionsSample = sh.getOptions(caller.sqlConnection, "sample")
        sample, index = pick.pick(optionsSample, _("Please choose a sample to attach analyses to."))

        sampleId = sample["id_sample"]

    # Select one ore more analyses.
    try:
        optionsAnalyses = sh.getOptions(caller.sqlConnection, "analysis")
        analyses = pick.pick(
            optionsAnalyses
          , _("Please choose on or more analyses.")
          , multiselect = True
        )
    except Exception as e:
        print(_(f"Error in collecting options for attachable analyses."))

    # TODO: One line list comprehension
    analysesDictianories = [t[0] for t in analyses]

    analysesIds = [d["id_analysis"] for d in analysesDictianories]

    analysesStr = ", ".join([str(i) for i in analysesIds])

    # Get procedures and measurands for these analyses.
    analysesInfo = si.fetchData(
        caller.sqlConnection
      , f"SELECT * FROM `analysis_procedure_measurand` WHERE id_analysis IN ({analysesStr})"
    )

    # Loop over all of these lines. Attach them one by one.
    # That way contrary to SELECT INTO info about the inserts ends up in the logs.

    # The list of keys stays the same for every line.
    listOfKeys = [
        "id_result"
      , "id_sample"
      , "id_measurand"
      , "id_analysis"
      , "id_procedure"
      , "id_unit"
      , "calculation"
    ]

    for a in analysesInfo:

        # Auto generate value for id_result. Simply a running number.
        resultPK = si.getPrimaryKey(caller.sqlConnection, "result")
        oldMax = si.fetchData(
            caller.sqlConnection
          , f"SELECT MAX({resultPK}) AS oldMax FROM `result`"
        )[0]["oldMax"]
        newMax = n.getNextNumber(oldMax, "running")

        # For readability get some values here.
        measurandId = a["id_measurand"]
        analysisId = a["id_analysis"]
        procedureId = a["id_procedure"]

        listOfValues = [
            newMax  # id_result: Calculated just now.
          , sampleId  # id_sample: Known from above.
          , measurandId  # id_measurand
          , analysisId  # id_analysis
          , procedureId  # id_procedure
            # id_unit: Known but can be overwritten later.
          , si.fetchData(
                caller.sqlConnection
              , f"SELECT id_unit FROM `procedure_measurand` " +
                f"WHERE id_procedure = {procedureId} AND id_measurand = {measurandId}"
            )[0]["id_unit"]
            # calculation: Set when creating a procedure.
          , si.fetchData(
                caller.sqlConnection
              , f"SELECT calculation FROM `procedure_measurand` " +
                f"WHERE id_procedure = {procedureId} AND id_measurand = {measurandId}"
            )[0]["calculation"]
        ]

        # Execute the insert.
        si.genericInsert(caller.sqlConnection, "result", listOfKeys, listOfValues, True)



# Generic attach.
def attachRelation(caller, relationTable):

    # Get information about the relation table.
    import sql_interop as si
    # Fetch the meta table.
    tableRefs = si.fetchData(
        caller.sqlConnection
      , si.buildQueryString(
            "./sql/GET_TABLE_REFS.SQL"
          , {"table": relationTable}
        )
    )

    # All these columns need to be filled.
    keyList = [
        d["Field"] for d in
        si.fetchData(caller.sqlConnection, f"SHOW COLUMNS FROM `{relationTable}`;")
    ]

    # Identify primary key and its current maximum value.
    pk = si.getPrimaryKey(caller.sqlConnection, relationTable)
    currentMaxPK = si.fetchData(
        caller.sqlConnection, f"SELECT MAX({pk}) AS currentMax FROM `{relationTable}`;"
    )[0]["currentMax"]

    # For every reference to another table an option list needs to be compiled.
    import sql_helpers as sh  # For compiling list of options.
    import pick  # For having the user pick.
    import mariadb  # For error handling of sql related problems.

    # Loop over all references.
    selections = []  # Fill by user selections.
    for ref in tableRefs:

        # Make sure all the keys needed are present.
        try:
            refToTable = ref["refToTable"]
            refToColumn = ref["refToColumn"]
            referencingColumn = ref["referencingCol"]
        except KeyError as e:
            print(f"Problem in compiling options list for generic attach. Key not found: {e}.")

        # Grab all the options. View are not allowed. In view columns can have different names.
        try:
            optionList = sh.getOptions(caller.sqlConnection, refToTable, viewAllowed = False)
        except mariadb.ProgrammingError as e:
            print(f"Compiling list of options failed because of an sql error ({e}).")
            return -1

        # Have the user pick one.
        sel, i = pick.pick(optionList, f"Please pick a record from table {refToTable}.")

        selections.append(sel)

    # Prepare the values.
    valueList = []  # Empty list to be filled.
    import numbering as n  # To auto generate numbers.

    # Loop over all keys.
    for k in keyList:
        # Is k the primary key?
        if k == pk:
            valueList.append(n.getNextNumber(currentMaxPK))
        # Fill by user?
        elif k not in [d["referencingCol"] for d in tableRefs]:
            valueList.append(input(f"Please input a value for field {k}: "))
        # Other values where chosen above.
        else:
            # Check the dictianories from the selections.
            for d in selections:
                # See if you can find a value to the required key in d.
                try:
                    valueList.append(d[k])
                # If not keep going.
                except KeyError:
                    pass

    # Execute the insert.
    try:
        si.genericInsert(caller.sqlConnection, relationTable, keyList, valueList)
    except Exception as e:
        print(f"Could not insert the n to m relation. Error: {e}.")
        print("Keys and values were:")
        print(keyList)
        print(valueList)
