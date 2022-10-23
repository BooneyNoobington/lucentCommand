#!/bin/env Rscript

# Calculate mean of arbitrary inputs.
args = commandArgs(trailingOnly = TRUE)

# Calculate mean.
print(as.numeric(args))
returnValue <- mean(as.numeric(args))

print(returnValue)

quit()
