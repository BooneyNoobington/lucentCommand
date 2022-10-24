/* Query for the biggest order related sample number. */

SELECT            MAX(X.NO_SAMPLE_IN_ORDER)
FROM              SAMPLE S
            JOIN  SAMPLE_ORDER X
              ON  X.ID_SAMPLE = S.ID_SAMPLE
WHERE             X.ID_ORDER = {ID_ORDER}
