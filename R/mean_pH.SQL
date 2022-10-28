SELECT              value
FROM                `result_raw`
WHERE               id_sample = {sample.id}
                AND id_procedure = {procedure.id}
                AND id_measurand = {measurand.id}
                AND accepted IS TRUE  -- Compute only accepted values.
;
