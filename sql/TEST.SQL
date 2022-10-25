/* Query for existing (?) user / person. */

SELECT          *
FROM            `person`
WHERE           LOWER(unix_account) = LOWER('{reciever1}')
            OR  LOWER(given_name) = LOWER('{reciever2}')
            OR  LOWER(surname) = LOWER('{reciever3}')
