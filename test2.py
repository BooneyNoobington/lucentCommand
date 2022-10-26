#!/bin/env python3

import sample

import sqlite_interop

import register as r

sqlConnection = sqlite_interop.databaseConnection("/home/grindel/Entwicklung/lucentLIMS_data_dir/lucent_0.0.1.sqlite.db")

try:
  print(r.getId(sqlConnection, "SPOT", {"name": "Kühlungsborn, Germany; the beach", "type": "beach"}))  # Expecting 2.
except Exception as e:
  print(e)
