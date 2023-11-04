from DatabaseManager import *
import params
import sys
import requests
import psycopg2
import json

cursor,conn = databaseConnection()
if cursor == None:
    print("Errore nello stabilire la connessione col server")
    sys.exit()

print("TUTTO OK :)")
