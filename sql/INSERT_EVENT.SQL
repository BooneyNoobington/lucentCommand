/* Insert an event into event table. */

INSERT INTO
EVENT (
    ID_EVENT
  , ID_FOREIGN
  , CONCERNED_TABLE
  , NAME
  , TYPE
  , DESCRIPTION
  , START_TIME
  , STOP_TIME
)

VALUES (
    {ID_EVENT}
  , {ID_FOREIGN}
  , {CONCERNED_TABLE}
  , {NAME}
  , {TYPE}
  , {DESCRIPTION}
  , {START_TIME}
  , {STOP_TIME}
);
