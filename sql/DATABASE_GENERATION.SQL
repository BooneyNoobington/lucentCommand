/* Generate database, user and tables for lucentLIMS
This script needs to be run as root.
Warning! This script is designed for the initial creation.
It will overwrite all existing databases with the name "lucent". */

SET FOREIGN_KEY_CHECKS = 0;     -- Since all tables are to be recreated
                                -- These checks can be safely ignored.

/* Initial database generation. */
CREATE OR REPLACE DATABASE lucent CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;

/* Inital user generation. */
create or replace user 'lucent'@'localhost' identified via 'unix_socket';
-- Only neccessary if SQL_MODE does not have NO_AUTO_CREATE_USER set
grant usage on lucent.* to 'lucent'@'localhost' identified via 'unix_socket';
grant all privileges on lucent.* to 'lucent'@'localhost';
flush privileges;

/* Databases */

use lucent;



-- Series 0: Misc.
CREATE OR REPLACE TABLE `possible_value`
(
    id_possible_value INTEGER PRIMARY KEY NOT NULL
  , concerning_table VARCHAR(50)
  , concerning_column VARCHAR(50)
  , value VARCHAR(100)
);

CREATE OR REPLACE TABLE `event`
(
    id_event INTEGER PRIMARY KEY UNIQUE NOT NULL
  , identifier VARCHAR(50) NOT NULL
  , class VARCHAR(20) NOT NULL
  , moment DATETIME NOT NULL
  , id_foreign INTEGER NOT NULL
  , concerning_table VARCHAR(50)
);

CREATE OR REPLACE TABLE `organisation`
(
    id_organisation INTEGER PRIMARY KEY NOT NULL
  , identifier VARCHAR(50) UNIQUE
  , short_identifier VARCHAR(15)
);

CREATE OR REPLACE TABLE `person`
(
    id_person INTEGER PRIMARY KEY UNIQUE NOT NULL
  , id_address INTEGER REFERENCES `address` (id_address)
  , id_organisation INTEGER REFERENCES `organisation` (id_organisation)
  , given_name VARCHAR(50) NOT NULL
  , surname VARCHAR(50) NOT NULL
  , unix_account VARCHAR(50) UNIQUE
);

CREATE OR REPLACE TABLE `message`
(
    id_message INTEGER PRIMARY KEY UNIQUE NOT NULL
  , sender VARCHAR(20) NOT NULL REFERENCES `person` (unix_account)
  , reciever VARCHAR(20) NOT NULL REFERENCES `person` (unix_account)
  , subject VARCHAR(250) NOT NULL
  , message VARCHAR(500) NOT NULL
  , read_status BOOLEAN NOT NULL DEFAULT 0
);


-- Series 1: procedures.

CREATE OR REPLACE TABLE `sop`
(
    id_sop INTEGER PRIMARY KEY NOT NULL
  , identifier VARCHAR(40) UNIQUE NOT NULL
  , active BOOLEAN NOT NULL
  , file_path VARCHAR(500)
  , url VARCHAR(500)
  , CONSTRAINT file_or_url_not_null CHECK (
        file_path is not null or url is not null
    )
);


CREATE OR REPLACE TABLE `procedure`
(
    id_procedure INTEGER PRIMARY KEY UNIQUE NOT NULL
  , identifier VARCHAR(50) NOT NULL
  , iteration DATETIME NOT NULL
  , active BOOLEAN NOT NULL
  , description VARCHAR(250)
  , id_sop INTEGER REFERENCES `sop` (id_sop)
    -- Name (and version) alone don't have to be unique but in combination they are.
  , CONSTRAINT ident_iter_unique UNIQUE(identifier, iteration)
);

-- A procedure can depend on multiple other procedures.
CREATE OR REPLACE TABLE `procedure_procedure`
(
    id_procedure_procedure INTEGER PRIMARY KEY UNIQUE NOT NULL
  , id_depending_procedure INTEGER NOT NULL REFERENCES `procedure` (id_procedure)
  , id_dependency_procedure INTEGER NOT NULL REFERENCES `procedure` (id_procedure)
);


-- A procedure is linked to one or more people with differenz responsibilities.
CREATE OR REPLACE TABLE `procedure_person`
(
    id_procedure_person INTEGER PRIMARY KEY UNIQUE NOT NULL
  , id_procedure INTEGER NOT NULL REFERENCES `procedure` (id_procedure)
  , id_person INTEGER NOT NULL REFERENCES `person` (id_person)
    -- What job does this person have regarding the procedure.
  , role VARCHAR(40) NOT NULL
    -- All of these attributes combined are unique.
  , CONSTRAINT person_proc_job_unique UNIQUE(id_procedure, id_person, role)
);

CREATE OR REPLACE TABLE `device`
(
    id_device INTEGER PRIMARY KEY UNIQUE NOT NULL
  , identifier VARCHAR(50) NOT NULL
  , number INTEGER NOT NULL
  , id_organisation INTEGER REFERENCES `organisation` (id_organisation)  -- Manufacturer.
  , active BOOLEAN NOT NULL DEFAULT TRUE
  , CONSTRAINT name_and_number_unqiue UNIQUE(identifier, number)
);

CREATE OR REPLACE TABLE `procedure_device`
(
    id_procedure_device INTEGER PRIMARY KEY UNIQUE NOT NULL
  , id_procedure INTEGER NOT NULL REFERENCES `procedure` (id_procedure)
  , id_device INTEGER NOT NULL REFERENCES `device` (id_device)
);

CREATE OR REPLACE TABLE `matrix`
(
    id_matrix INTEGER PRIMARY KEY UNIQUE NOT NULL
  , identifier VARCHAR(20) NOT NULL UNIQUE
  , class VARCHAR(25) NOT NULL  -- General type of the matrix. Solid object, fluid, soil ...
  , description VARCHAR(250)
);


CREATE OR REPLACE TABLE `sampleclass`
(
    id_sampleclass INTEGER PRIMARY KEY UNIQUE NOT NULL
  , identifier VARCHAR(20) NOT NULL UNIQUE
  , description VARCHAR(250)
);


CREATE OR REPLACE TABLE `procedure_matrix`
(
    id_procedure_matrix INTEGER PRIMARY KEY UNIQUE NOT NULL
  , id_procedure INTEGER NOT NULL REFERENCES `procedure` (id_procedure)
  , id_matrix INTEGER NOT NULL REFERENCES `matrix` (id_matrix)
  , CONSTRAINT procedure_matrix_unqiue UNIQUE(id_procedure, id_matrix)
);


CREATE OR REPLACE TABLE `procedure_sampleclass`
(
    id_procedure_sampleclass INTEGER PRIMARY KEY UNIQUE NOT NULL
  , id_procedure INTEGER NOT NULL REFERENCES `procedure` (id_procedure)
  , id_sampleclass INTEGER NOT NULL REFERENCES `sampleclass` (id_sampleclass)
  , CONSTRAINT procedure_sampleclass_unqiue UNIQUE(id_procedure, id_sampleclass)
);


CREATE OR REPLACE TABLE `unit`
(
    id_unit INTEGER PRIMARY KEY UNIQUE NOT NULL
  , identifier VARCHAR(40) NOT NULL
  , formula VARCHAR(20) NOT NULL
  , description VARCHAR(50)
);


CREATE OR REPLACE TABLE `measurand`
(
    id_measurand INTEGER PRIMARY KEY UNIQUE NOT NULL
  , identifier VARCHAR(20) UNIQUE NOT NULL
  , cas VARCHAR(20)
);


CREATE OR REPLACE TABLE `procedure_measurand`
(
    id_procedure_measurand INTEGER PRIMARY KEY UNIQUE NOT NULL
  , id_procedure INTEGER NOT NULL REFERENCES `procedure` (id_procedure)
  , id_measurand INTEGER NOT NULL REFERENCES `measurand` (id_measurand)
  , id_unit INTEGER NOT NULL REFERENCES `unit` (id_unit)
  , error DOUBLE NOT NULL
  , error_class VARCHAR(9) NOT NULL
  , error_unit INTEGER NOT NULL REFERENCES `unit` (id_unit)
  , calculation VARCHAR(15)  -- TODO: Deprecate.
);

-- Is set up when procedure is defined.
-- Governs which result is derived by which raw value and by which calculation.
CREATE OR REPLACE TABLE `calculation`
(
    -- Auto generated primary key.
    id_calculation INTEGER PRIMARY KEY UNIQUE NOT NULL
    -- Values can be calculated in a different way depending on which method of
    -- measurement was used.
  , id_procedure INTEGER NOT NULL REFERENCES `procedure` (id_procedure)
    -- Script file can be any script language which is installed on the server
    -- and is able to manipulate records in an rdbms.
  , script_file VARCHAR(250) NOT NULL
    -- What ends up in the table `result`.
  , measurand_result INTEGER NOT NULL REFERENCES `measurand` (id_measurand)
    -- Which input parameters are necessary? If more than one this
    -- table simply has multiple rows for each "measurand_result" (n to m).
  , measurand_input INTEGER NOT NULL REFERENCES `measurand` (id_measurand)
    -- An input can consist of various groups. Like raw values for
    -- variable a and some other values for variable b.
    -- The c could be mean(a) - mean(b).
    -- These groups are defined here.
  , argument_group INTEGER NOT NULL
);

-- An analysis is a collection of measurands from one or more procedures.
CREATE OR REPLACE TABLE `analysis`
(
    id_analysis INTEGER PRIMARY KEY UNIQUE NOT NULL
  , identifier VARCHAR(50) NOT NULL
  , iteration DATETIME NOT NULL
    -- Name (and version) alone don't have to be unique. But in combination
    -- they should be.
  , CONSTRAINT ident_iter_unique UNIQUE(identifier, iteration)
);

-- Connect analyses and procedures.
CREATE OR REPLACE TABLE `analysis_procedure_measurand`
(
    id_analysis_procedure_measurand INTEGER PRIMARY KEY UNIQUE NOT NULL
  , id_procedure INTEGER REFERENCES `procedure` (id_procedure)
  , id_analysis INTEGER REFERENCES `analysis` (id_analysis)
  , id_measurand INTEGER REFERENCES `measurand` (id_measurand)
  , CONSTRAINT pam_combo_unique UNIQUE(id_procedure, id_analysis, id_measurand)
);



-- Series 2: Samples

CREATE OR REPLACE TABLE `city`
(
    id_city INTEGER PRIMARY KEY UNIQUE NOT NULL
  , identifier VARCHAR(60) NOT NULL UNIQUE
);

CREATE OR REPLACE TABLE `district`
(
    id_district INTEGER PRIMARY KEY UNIQUE NOT NULL
  , identifier VARCHAR(60) NOT NULL UNIQUE
  , id_city INTEGER REFERENCES `city` (id_city)
  , zip INTEGER NOT NULL
);

CREATE OR REPLACE TABLE `street`
(
    id_street INTEGER PRIMARY KEY UNIQUE NOT NULL
  , identifier VARCHAR(100) NOT NULL
  , id_district INTEGER REFERENCES `district` (id_district)
  , CONSTRAINT one_street_per_district UNIQUE(identifier, id_district)
);

CREATE OR REPLACE TABLE `address`
(
    id_address INTEGER PRIMARY KEY UNIQUE NOT NULL
  , id_street INTEGER REFERENCES `street` (id_street)
  , house_number INTEGER NOT NULL
  , house_number_addition VARCHAR(5)
    -- Make sure that there is only one house per street.
  , CONSTRAINT house_number_addition_street UNIQUE(
        house_number
      , house_number_addition
      , id_street
    )
);

CREATE OR REPLACE TABLE `site`
(
    id_site INTEGER PRIMARY KEY UNIQUE NOT NULL
  , identifier VARCHAR(20) UNIQUE NOT NULL
  , class VARCHAR(30) NOT NULL
  , id_district INTEGER REFERENCES `district` (id_district)
  , id_address INTEGER REFERENCES `address` (id_address)
);

CREATE OR REPLACE TABLE `body_of_water`
(
    id_body_of_water INTEGER PRIMARY KEY UNIQUE NOT NULL
  , identifier VARCHAR(45) UNIQUE NOT NULL
  , class VARCHAR(30) NOT NULL
);

CREATE OR REPLACE TABLE `spot`
(
    id_spot INTEGER PRIMARY KEY NOT NULL
  , identifier VARCHAR(20) UNIQUE NOT NULL
  , id_site INTEGER REFERENCES `site` (id_site)
  , id_body_of_water INTEGER REFERENCES `body_of_water` (id_body_of_water)
  , class VARCHAR(30) NOT NULL
);

-- For choosing a spot interactively, information about the site is also
-- Important. This view will be prefered when lucent is asking
-- interactively for a spot.
CREATE OR REPLACE VIEW `attach_spot` AS
  SELECT        `spot`.id_spot
              , `spot`.identifier AS "name of spot"
              , `spot`.class AS "class of spot"
              , `site`.identifier AS "name of site"
              , `site`.class AS "class of site"
              , `body_of_water`.identifier AS "body of water"
  FROM          `spot`
          JOIN  `site`
            ON  `site`.id_site = `spot`.id_site
          JOIN  `body_of_water`
            ON  `body_of_water`.id_body_of_water = `spot`.id_body_of_water
;

-- A tool to loosely group samples together. Mostly for lab internal use.
CREATE OR REPLACE TABLE `samplegroup`
(
    id_samplegroup INTEGER PRIMARY KEY UNIQUE NOT NULL
  , identifier VARCHAR(30) NOT NULL UNIQUE
  , description VARCHAR(250) NOT NULL
);

-- More fine grained grouping.
CREATE OR REPLACE TABLE `samplesubgroup`
(
    id_samplesubgroup INTEGER PRIMARY KEY UNIQUE NOT NULL
  , identifier VARCHAR(30) NOT NULL UNIQUE
  , id_samplegroup INTEGER NOT NULL REFERENCES `samplegroup` (id_samplegroup)
);

-- One of the most important tables. The center for all measurements
CREATE OR REPLACE TABLE `sample`
(
    -- (Internal) Number of the sample. More clunky than a readable number.
    id_sample INTEGER PRIMARY KEY UNIQUE NOT NULL
    -- The identifier is not unique. To the user it will be presented as a
    -- concat between sample group identifier + sample subgroup identifier and + sample identifier.
  , id_samplesubgroup INTEGER NOT NULL REFERENCES `samplesubgroup` (id_samplesubgroup)
  , identifier INTEGER
    -- Where was the sample taken?
  , id_spot INTEGER NOT NULL
    -- What material was sampled?
  , id_matrix INTEGER NOT NULL REFERENCES `matrix` (id_matrix)
    -- How did the sampling happen? TODO: Maybe rename just to sampling or sampling_class?
  , id_sampleclass INTEGER NOT NULL REFERENCES `sampleclass` (id_sampleclass)
    -- Make sure that in each subgroup every readable number (identifier) exists only once.
  , CONSTRAINT ident_and_subg_unique UNIQUE(identifier, id_samplesubgroup)
  , CONSTRAINT `id_spot`
      FOREIGN KEY (id_spot) REFERENCES `spot` (id_spot)
      ON DELETE CASCADE
      ON UPDATE RESTRICT
);

-- A nicer view for interactivity.
  CREATE OR REPLACE VIEW `attach_sample` AS
    SELECT          s.id_sample
                  , sc.identifier AS "sampleclass"
                  , sp.identifier AS "spot"
                  , si.identifier AS "site"
                  , d.identifier AS "district"
                  , c.identifier AS "city"
                  , bw.identifier AS "body of water"
                  , ssg.identifier AS "sample subgroup"
                  , sg.identifier AS "sample group"
                  , m.identifier AS "matrix"
    FROM            `sample` s
              JOIN  `samplesubgroup` ssg
                ON  ssg.id_samplesubgroup = s.id_samplesubgroup
              JOIN  `samplegroup` sg
                ON  sg.id_samplegroup = ssg.id_samplegroup
              JOIN  `sampleclass` sc
                ON  sc.id_sampleclass = s.id_sampleclass
              JOIN  `matrix` m
                ON  m.id_matrix = s.id_matrix
              JOIN  `spot` sp
                ON  sp.id_spot = s.id_spot
              JOIN  `site` si
                ON  si.id_site = sp.id_site
              JOIN  `district` d
                ON  d.id_district = si.id_district
              JOIN  `city` c
                ON  c.id_city = d.id_city
              JOIN  `body_of_water` bw
                ON  bw.id_body_of_water = sp.id_body_of_water
  ;

--- Series 3: Results.

-- Important: Raw results are inserted in an somewhat unplanned manner.
-- Every time a device produces a result, it can be individually inserted
-- into the database.

-- TODO: Maybe make it so that values can directly be inserted into `result`.
CREATE OR REPLACE TABLE `result_raw`
(
    id_result_raw INTEGER PRIMARY KEY UNIQUE NOT NULL
    -- Which sample was this measurement taken in?
  , id_sample INTEGER NOT NULL REFERENCES `sample` (id_sample)
    -- What was measured?
  , id_measurand INTEGER NOT NULL REFERENCES `measurand` (id_measurand)
    -- How was it measured?
  , id_procedure INTEGER NOT NULL REFERENCES `procedure` (id_procedure)
    -- From wich device comes the result?
  , id_device INTEGER NOT NULL REFERENCES `device` (id_device)
    -- When was the measurement aquired?
  , moment DATETIME NOT NULL
    -- Who did the measurement?
  , id_person INTEGER NOT NULL REFERENCES `person`(id_person)
    -- What was the actual result and which unit has it?
    -- (Uncertainty is known by method.)
  , value DOUBLE NOT NULL
  , id_unit INTEGER NOT NULL REFERENCES `unit` (id_unit)
    -- Raw results need to be either accepted or declined
    -- before a calculation can be made.
    -- TODO: (Semi) Non enforceable rule. The calculation alone script decides
    -- which raw values it uses.
  , accepted BOOLEAN NOT NULL DEFAULT 0  -- By default now value is accepted.
);


-- This table is inserted in advance. It results from a connection between a
-- sample and its analyses.
CREATE OR REPLACE TABLE `result`
(
    id_result INTEGER PRIMARY KEY UNIQUE NOT NULL
    -- Which sample was this measurement taken in?
  , id_sample INTEGER NOT NULL REFERENCES `sample` (id_sample)
    -- What was measured?
  , id_measurand INTEGER NOT NULL REFERENCES `measurand` (id_measurand)
    -- How was it measured? Strictly a reference to a procedure is not neccessary
    -- here, since everything about the procedures can be derived from the analyses.
  , id_analysis INTEGER NOT NULL REFERENCES `analysis` (id_analysis)
  , id_procedure INTEGER NOT NULL REFERENCES `procedure` (id_procedure)
    -- From wich device comes the result? This is also not known at insert time since
    -- any procedure can be valid for multiple devices.
  , id_device INTEGER REFERENCES `device` (id_device)
    -- Who did the measurement? Not clear on insert time.
  , id_person INTEGER REFERENCES `person`(id_person)
    -- When was the measurement aquired? Not clear on insert time.
  , moment DATETIME
    -- What was the actual result and which unit has it?
    -- (Uncertainty is known by method.)
  , value DOUBLE  -- Null until calculated.
  , id_unit INTEGER NOT NULL REFERENCES `unit` (id_unit)  -- Can be overwritten.
    -- Point to a custom script that does the calculation.
  , calculation VARCHAR(60) NOT NULL
    -- Make sure that only one there is only one result for
    -- a given sample, measurand and procedure.
  , CONSTRAINT spm_unique UNIQUE(id_sample, id_procedure, id_measurand)
);


-- A readable overview for results.
CREATE OR REPLACE VIEW `readable_result` AS
  SELECT          r.id_result
                , r.id_sample
                , m.identifier AS "measurand"
                , a.identifier AS "analysis"
                , p.identifier AS "procedure"
                , d.identifier AS "device"
                , CONCAT(pe.given_name, ', ', pe.surname) AS "measured by"
                , r.moment AS "measured on"
                , r.value AS "result"
                , u.formula AS "unit"
                , r.calculation
  FROM            `result` r
            JOIN  `measurand` m
              ON  m.id_measurand = r.id_measurand
            JOIN  `analysis` a
              ON  a.id_analysis = r.id_analysis
            JOIN  `procedure` p
              ON  p.id_procedure = r.id_procedure
       LEFT JOIN  `device` d  -- Left join because device might be initially null.
              ON  d.id_device = r.id_device
       LEFT JOIN  `person` pe  -- Left join because experimentator might be unknown.
              ON  pe.id_person = r.id_person
            JOIN  `unit` u
              ON  u.id_unit = r.id_unit
;


-- Realize "tables" sample_analysis and sample_procedure as views. Performance ?!?
CREATE OR REPLACE VIEW `sample_analysis` AS
  SELECT DISTINCT       s.id_sample
                      , a.id_analysis
  FROM                  `sample` s
                  JOIN  `result` r
                    ON  r.id_sample = s.id_sample
                  JOIN  `analysis` a
                    ON  a.id_analysis = r.id_analysis
;

CREATE OR REPLACE VIEW `sample_procedure` AS
  SELECT DISTINCT       s.id_sample
                      , p.id_procedure
  FROM                  `sample` s
                  JOIN  `result` r
                    ON  r.id_sample = s.id_sample
                  JOIN  `procedure` p
                    ON  p.id_procedure = r.id_procedure
;

