SELECT          COLUMN_NAME as "referencingCol"
              , REFERENCED_TABLE_NAME as "refToTable"
              , REFERENCED_COLUMN_NAME as "refToColumn"
FROM            INFORMATION_SCHEMA.KEY_COLUMN_USAGE
WHERE           TABLE_NAME = '{table}'
            AND REFERENCED_TABLE_NAME IS NOT NULL
;
