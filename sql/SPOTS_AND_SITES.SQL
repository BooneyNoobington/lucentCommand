SELECT              `spot`.id_spot
                  , `spot`.identifier AS "spot"
                  , `site`.identifier AS "site"
FROM                `site`
              JOIN  `spot`
                ON  `spot`.id_site = `site`.id_site


