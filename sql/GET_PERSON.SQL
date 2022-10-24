/* Query for existing (?) user / person. */

SELECT          *
FROM            `person`
WHERE           LOWER(unix_account) = LOWER('{reciever}')
            OR  LOWER(given_name) = LOWER('{reciever}')
            OR  LOWER(surname) = LOWER('{reciever}')
