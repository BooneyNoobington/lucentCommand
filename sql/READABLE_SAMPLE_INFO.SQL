SELECT                S.ID_SAMPLE AS "distinct sample number"
                    , C.NAME || '·' || O.SHORT_IDENTIFIER || '·' || X.NO_SAMPLE_IN_ORDER AS "main number"
                    , E.START_TIME AS "planned sampling"
                    , O.NAME AS "most important order"                     

FROM                  SAMPLE S
                JOIN  SAMPLE_ORDER X
                  ON  X.ID_SAMPLE = S.ID_SAMPLE
                JOIN  `ORDER` O
                  ON  O.ID_ORDER = X.ID_ORDER
                JOIN  CAMPAIGN C
                  ON  C.ID_CAMPAIGN = S.ID_CAMPAIGN
           LEFT JOIN  (
                            SELECT *,   E.ID_FOREIGN AS "ID_SAMPLE"
                            FROM        EVENT E
                            WHERE       E.CONCERNED_TABLE = 'SAMPLE'
                                    AND E.NAME = 'sampling (planned)'
                      ) E
                  ON  E.ID_SAMPLE = S.ID_SAMPLE
               
WHERE                 "main number" IN(
                            SELECT "main number" FROM (
                                SELECT          C.NAME || '·' || O.SHORT_IDENTIFIER || '·' || X.NO_SAMPLE_IN_ORDER AS "main number"
                                              , MIN(X.PRIORITY) AS HIGHEST_PRIORITY
                                FROM            SAMPLE S
                                          JOIN  SAMPLE_ORDER X
                                            ON  X.ID_SAMPLE = S.ID_SAMPLE
                                          JOIN  `ORDER` O
                                            ON  O.ID_ORDER = X.ID_ORDER 
                                          JOIN  CAMPAIGN C
                                            ON  C.ID_CAMPAIGN = S.ID_CAMPAIGN
                                GROUP BY        S.ID_SAMPLE
                            )
                      )
