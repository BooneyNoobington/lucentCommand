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
    try:
        tableInfo = caller.config["tables"][relationTable]["attach rules"]
    except KeyError:
        print(f"Import for {relationTable} not configured.")
        return -1

    # Have the user choose.
    import sql_interop as si  # Fetch data, insert records.
    import sql_helpers as sh  # SQL-related helpers.
    import pick  # Choose from a list of options.

    # Collect options for records in the the master table.
    try:
        masterTableOptions = si.getOptions(
            caller.sqlConnection, tableInfo["options for"]["master table"]["table name"]
        )
    except KeyError:
        print("Error collection options for master table. Correctly configured?")
        return -1

    # Have the user pick one.
    try:
        masterTableChoice = pick.pick(
            masterTableOptions
          , tableInfo["options for"]["master table"]["choice text"]
          , multiselect = True
        )
    except KeyError:  # Choice text is optional.
        masterTableChoice = [t[0] for t in
            pick.pick(
                masterTableOptions, tableInfo["options for"]["master table"], multiselect = True)
            )
        ]

    # Collect options for records in the the detail table.
    try:
        detailTableOptions = si.getOptions(
            caller.sqlConnection, tableInfo["options for"]["detail table"]["table name"]
        )
    except KeyError:
        print("Error collection options for detail table. Correctly configured?")
        return -1

    # Have the user pick one.
    try:
        detailTableChoice = pick.pick(
            masterTableOptions
          , tableInfo["options for"]["detail table"]["choice text"]
          , multiselect = True
        )
    except KeyError:  # Choice text is optional.
        detailTableChoice = [t[0] for t in
            pick.pick(
                masterTableOptions, tableInfo["options for"]["detail table"], multiselect = True)
            )
        ]

    import pprint
    pprint.pprint(masterTableChoice)
    pprint.pprint(detailTableChoice)
