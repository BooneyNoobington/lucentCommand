# Function to calculate a mean of several pHs.
pH.mean <- function(pH.vec){

    # Transform log to concentration.
	concentration <- exp(-(pH.vec)/(log(exp(1))))

	# Compute mean. Ingore "not numbers".
	concentration.mean <- mean(concentration, na.rm = TRUE )

	# Re-transform to logarithm.
	concentration.mean.log <- -log(concentration.mean)

	return(concentration.mean.log)
}
