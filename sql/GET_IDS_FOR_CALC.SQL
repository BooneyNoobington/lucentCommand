SELECT DISTINCT         id_result
FROM                    `result`
WHERE                   id_sample = {currentSampleId}
                    AND id_procedure = {currentProcedureId}
                    AND id_measurand = {currentMeasurandId}
