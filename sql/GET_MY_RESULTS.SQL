SELECT              rr.id_sample AS "sample id"
                  , p.identifier AS "procedure"
                  , m.identifier AS "measurand"
                  , rr.value AS "raw result"
                  , u.formula AS "unit"
                  , rr.accepted AS "acceptance status"

FROM                `result_raw` rr  -- Start from here.
              JOIN  `measurand` m  -- More info about what was measured.
                ON  m.id_measurand = rr.id_measurand
              JOIN  `procedure` p  -- And how it was measured.
                ON  p.id_procedure = rr.id_procedure
              JOIN  `unit` u  -- Unit for value.
                ON  u.id_unit = rr.id_unit
              JOIN  `person` per  -- Which people are asscociated with the procedure?
                ON  per.id_person = p.id_person

WHERE               rr.id_sample = {sampleId}  -- Limit to currently used sample…
               AND  per.unix_account = '{unixAccount}'  -- … and user logged in.
;



              -- JOIN  `result` r
              --   ON      rr.id_sample = r.id_sample
              --       AND rr.id_procedure = r.id_procedure
              --       AND rr.id_measurand = r.id_measurand
