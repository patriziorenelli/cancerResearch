
import psycopg2
import pandas as pd
from io import StringIO
import params


# LE 2 CLOSURE SONO FONDAMENTALI PERCHE' LA CONNESSIONE USATA CHE VA IN ERRORE E' DA BUTTARE !! 
'''
Costruisce la struttura delle tabelle del database e richiama la funzione necessaria al riempimento delle tabelle di base
'''
def databaseConstruction():
    cursor,conn = databaseConnection()
    if cursor == None:
        print("FATAL ERROR")
        return cursor, conn

    errore = False
    check_table = "SELECT COUNT(*) FROM primary_site"

    try:
        cursor.execute(check_table)
        result = cursor.fetchone()
    except psycopg2.Error as db_error:
        if "non esiste" in str(db_error):
            # Procedo con la creazione delle tabelle 
                    cursor.close()
                    conn.close()
                    cursor, conn = databaseConnection()
                    # Carico le singole query da eseguire per creare le tabelle 
                    query = open("Schema.sql", "r").read()
                    query = query.split(";")
                    # Eseguo le singole query e controllo il loro risultato 
                    for x in query: 
                        try:
                            cursor.execute(x)
                            conn.commit()
                        except psycopg2.Error as db_error:
                            if "can't execute an empty query" not in str(db_error):
                                print("FATAL", db_error)
                                errore = True
                                cursor = None
                                conn = None
                                break
                    
                    if not errore:
                        print("Struttura del databse creata")    
                        if fillingBasicTable(cursor, conn):
                            print("Errore nella riempimento delle tabelle base")
                            cursor = None
                            conn = None
                    return cursor, conn
    return cursor,conn   
'''
Funzione per la creazione del database e la creazione delle sue tabelle 
 '''
def databaseCreation():
    try: 
        conn = psycopg2.connect(database = "postgres", user = params.user, password = params.password , host = params.host , port = params.port)
        conn.autocommit = True
        cursor = conn.cursor()
        sql = 'CREATE database "GDC"'
        cursor.execute(sql)
        print("Database creato")
        return databaseConstruction()
    except psycopg2.Error as db_error:
        print("Errore nella connesione al database")
        print("Dettaglio errore: ", db_error)
        return None, None

'''
Funzione che si occupa di gestire la creazione di una connessione con il database 
Se il database non esiste viene creato e vengono create tutte le tabelle necessarie 
'''
def databaseConnection():
    try: 
        # Crea una connessione al database PostgreSQL
        connection = psycopg2.connect(**params.db_params)
        # Crea un cursore per eseguire query SQL
        cursor = connection.cursor()
        # Inizia la transazione
        connection.autocommit = False 
        return cursor, connection
    except psycopg2.Error as db_error:
        # Se il database non esiste lo vado a creare 
        if "non esiste" in str(db_error) :
            print("DATABASE NON ESISTENTE" )
            return databaseCreation()
        else:
            print("Errore nella connesione al database")
            print("Dettaglio errore: ", db_error)
            return None 


'''
Funzione che si occupa di riempire le tabelle di base necessarie al funzionamento delle altre funzione
Sfrutta dei file contenuti nella cartella load contenenti i dati da caricare 
'''
def fillingBasicTable(cursor,conn):
    basicTable = ["primary_site", "biospecimen_type", "data_category", "data_type", "disease", "experimental_strategy", "gene_type"]
    basicQuery = "INSERT INTO public.{} VALUES (DEFAULT, '{}');"

    try: 
        for tab in basicTable:
            # dobbiamo aprire il relativo file e poi fare un for per le insert 
            #print( basicQuery.format(basicTable[0], "'Maria'")  )
            path = ('.\\load\\{}.txt').format(tab)
            ins = open( path, "r").read()
            ins = ins.split('\n')
            
            for val in ins:

                quer = basicQuery.format(tab, val )
                cursor.execute(quer)
                conn.commit()
    except:
        print("ERRORE FATALE NEL RIEMPIMENTO DELLE TABELLE")
        return True

    return False





