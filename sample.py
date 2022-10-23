#!/bin/env python3


# Function to compute the next readable number for the sample.
def getNextReadable(currentMax, computation = "running"):

  if currentMax is None:
    print(
      "Warning: No highest readable number could be determined \n" +
        "This warning should only appear once per order."
    )
    currentMax = 0

  # "running" means a generic running number (n = n + 1).
  if computation == "running":
    return currentMax + 1

  # Do not allow repeating digits as in 311 or 10222.
  elif computation == "no_repeating":

    # Start with the assumption that the next bigger integer
    # is a suitable candidate.
    candidate = currentMax + 1

    # As long as there are repeating digits (turning the stringified form of
    # candidate into a set removes doubles) add one.
    while len(set(str(candidate))) < len(str(candidate)):
      candidate = candidate + 1

    return candidate

  # Do not allow permutations of the new max to be smaller numbers.
  # E.g. if you have 124 you can't have 421 or 241 or 214 ...
  elif computation == "no_swaps":

    import itertools  # For creating permutations.

    # Start with the assumption that the next bigger integer
    # is a suitable candidate.
    candidate = currentMax + 1

    # Create permutation for current string.
    sPermutations = [''.join(p) for p in itertools.permutations(str(candidate))]

    # Check wether a permutation of candidate is a smaller number.
    while any(
      item in str(list(range(1, currentMax))) for item in sPermutations
    ):

      # If so try the next.
      candidate = candidate + 1

      # Also recreate permutation.
      sPermutations = [
        ''.join(p) for p in itertools.permutations(str(candidate))
      ]

    return  candidate

  # Allow neither repeating nor swappable digits.
  elif computation == "save":

    import itertools  # For creating permutations.

    # Start with the assumption that the next bigger integer
    # is a suitable candidate.
    candidate = currentMax + 1

    # Create permutation for current string.
    sPermutations = [''.join(p) for p in itertools.permutations(str(candidate))]

    # Check wether a permutation of candidate is a smaller number.
    while any(
      item in str(list(range(1, currentMax))) for item in sPermutations
    ) or len(set(str(candidate))) < len(str(candidate)):

      # If so try the next.
      candidate = candidate + 1

      # Also recreate permutation.
      sPermutations = [
        ''.join(p) for p in itertools.permutations(str(candidate))
      ]

    return  candidate

  # Anything else was probably a typo.
  else:
    raise ValueError("Computation type \"" + computation + "\" is not defined.")



# Function to register a sample from a given yaml file.
def registerSamplesFromYAML(sqliteConnection, yamlFile, verbose = False):

  # Overall imports.
  import yaml_interop as yi
  import sqlite_interop as si
  import import_helpers as ih
  import helpers

  # Get new samples from YAML file.
  try:
    newSamples = yi.loadDictianories(yamlFile)
  except Exception as e:
    print("While trying to load YAML sample info into lucent this happend:")
    print(e)
    exit(1)  # This totally has to work.

  for s in newSamples:

    try:
      if verbose: print("Processing sample…")
      if verbose: print(s)
    except Exception as e:
      print(e)
      exit(1)

    # Get the spot id. Can be supplied as id or as name. getForeignKey handles
    # both.
    spotId = ih.getForeignKey(s, "spot", sqliteConnection = sqliteConnection)


    # Same for matrix.
    if verbose: print("Getting matrix id…")

    matrixId = ih.getForeignKey(
        s
      , "matrix"
      , "type"
      , sqliteConnection = sqliteConnection
    )

    if verbose: print("Got: " + str(matrixId))


    # And for type.
    if verbose: print("Getting type id…")

    typeId = ih.getForeignKey(s, "type", sqliteConnection = sqliteConnection)

    if verbose: print("Got: " + str(typeId))


    # Anf for campaign.
    if verbose: print("Getting campaign id…")

    campaignId = ih.getForeignKey(s, "campaign", sqliteConnection = sqliteConnection)

    if verbose: print("Got: " + str(campaignId))


    # Retrieve sample id.

    if verbose: print("Looking up biggest sample id so far …")

    maxSampleId = si.fetchData(
        sqliteConnection
      , "SELECT MAX(ID_SAMPLE) FROM SAMPLE"
    )

    if verbose: print("Found: " + str(maxSampleId[0]["MAX(ID_SAMPLE)"]))

    # Get next bigger integer.
    try:
      newMaxSampleId = int(maxSampleId[0]["MAX(ID_SAMPLE)"]) + 1
    except TypeError:
      if verbose: print(
         "Query for highest event id returned none." +
           "\nAssuming 0. This warning should only appear once!"
      )
      maxSampleId = 0
      newMaxSampleId = maxSampleId + 1


    # Execute insertion.
    if verbose: print("Inserting " + str(newMaxSampleId) + " …")

    si.executeStatement(
        sqliteConnection
      , si.buildQueryString(
            "./sql/INSERT_SAMPLE.SQL"
          , {
                "ID_SAMPLE": newMaxSampleId
              , "ID_SPOT": spotId
              , "ID_CAMPAIGN": campaignId
            }
        )
    )


    # Insert into conenction table (n-m-sample-order).

    if verbose: print("Attaching orders…")

    for o in s["order"]:

      if verbose: print("Attaching: ")
      if verbose: print(o)

      # Fetch the id if it wasn't supplied.
      try:
        orderId = o["id"]
      except KeyError:
        orderId = si.fetchData(
            sqliteConnection
          , "SELECT ID_ORDER FROM `ORDER` WHERE NAME = \'" + o["name"] + "\'"
        )[0]["id_order"]
      except Exception as e:
        print(
          "While trying to connect sample "
            + str(newMaxSampleId) + " to an order this exception was raised."
        )
        print(e)

      # Get the highest order specific sample number.
      biggestOrderSampleNumber = si.fetchData(
          sqliteConnection
        , "SELECT MAX(NO_SAMPLE_IN_ORDER) FROM SAMPLE_ORDER X " +
            "WHERE X.ID_ORDER = " + str(orderId)
      )[0]["MAX(NO_SAMPLE_IN_ORDER)"]

      # Calculate the next biggest one.
      newOrderSampleNumber = getNextReadable(biggestOrderSampleNumber, "save")

      # Create the connection.
      try:
        si.executeStatement(
            sqliteConnection
          , si.buildQueryString(
                "./sql/INSERT_SAMPLE_ORDER_JOIN.SQL"
              , {
                    "ID_SAMPLE": newMaxSampleId
                  , "ID_ORDER": orderId
                  , "PRIORITY": o["priority"]
                  , "NO_SAMPLE_IN_ORDER": newOrderSampleNumber
                }
            )
        )
      except KeyError:
        print("Connecting sample to order failed. Was a priority supplied?")


    if verbose: print("Attaching events…")


    # Attach events to registered samples.
    for e in s["event"]:

      if verbose: print("Attaching:")
      if verbose: print(e)

      # First get the biggest id from the events table.
      currentMaxId = si.fetchData(
          sqliteConnection
        , "SELECT MAX(ID_EVENT) FROM EVENT"
      )[0]["MAX(ID_EVENT)"]

      try:
        newMaxId = currentMaxId + 1
      except TypeError:
        if verbose: print(
          "Query for highest event id returned none." +
            "\nAssuming 0. This warning should only appear once!"
        )
        currentMaxId = 0
        newMaxId = currentMaxId + 1

      # Invoke the insert query.
      si.executeStatement(
          sqliteConnection
        , si.buildQueryString(
              "./sql/INSERT_EVENT.SQL"
            , {
                  "ID_EVENT": newMaxId
                , "ID_FOREIGN": newMaxSampleId
                , "CONCERNED_TABLE": "\'SAMPLE\'"
                , "NAME": "\'" + e["name"] + "\'"
                , "TYPE": "\'user\'"
                , "DESCRIPTION": "\'" + e.get("description", "") + "\'"
                , "START_TIME": "\'" + e["start_time"] + "\'"
                , "STOP_TIME": "\'" + e.get("stop_time", "") + "\'"
              }
          )
      )


def addOneAndOne(a, b):
  return(a + b)
