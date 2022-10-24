#!/bin/env python3

# Function to compute the next readable number for the sample.
def getNextNumber(currentMax, computation = "running"):

  # Handle the problem that no current max can be determined
  # for first dataset in table.
  if currentMax is None:
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
