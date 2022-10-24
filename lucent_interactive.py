#!/bin/env python3

# Functions for the lucent terminal.

def load_samples(sqliteConnection):

  import sqlite_interop as si

  return si.fetchData(sqliteConnection, "SELECT * FROM SAMPLE")
