from DatabaseManager import *
from DatabaseGenericInteraction import *
import params 
import sys
import requests
import psycopg2
import json
import csv


# RIABILITARE I TRY EXCEPT PRIMA DI METTERE IN PROD 
# VEDERE CHECK PARTE !!!!  E LA FUNZIONE  insertNewSamples


# Funzione per scaricare e processare i dati di espressione da GDC
'''
Gli passo params in modo da potervi accedere 
'''
def download_and_process_expression_data(param):

    #try:
        # Creo connessione con il database 
        cursor, conn = databaseConnection()
        if cursor == None or conn == None:
            print("Impossibile connettersi al database")
            return 
        else: 
            print("Connessione riuscita")

        conn.autocommit = False

        # URL dell'API GDC per scaricare i file corrispondenti alle analisi
        gdc_api_url = "https://api.gdc.cancer.gov/files"

        # Download dei dati
        filters = {
            "op": "and",
            "content": [
                # Filtro riguardante il sito primario della malattia che vogliamo analizzare
                {
                    "op": "=",
                    "content": {
                        "field": "cases.primary_site",
                        "value": "bronchus and lung"
                    }
                },
                # Filtro riguardante il tipo di dati che vogliamo analizzare
                {
                    "op": "in",
                    "content": {
                        "field": "data_type",
                        "value": ["Gene Expression Quantification"]   # clsProtein Expression Quantification
                    }
                },

                # Filtro riguardante l'accesso dei dati
                {
                    "op": "=",
                    "content": {
                        "field": "access",
                        "value": "open"
                    }
                },

                # Filtro riguardante il formato del file su cui è riportata l'analisi
                {
                    "op": "=",
                    "content": {
                        "field": "data_format",
                        "value": "TSV"
                    }
                }
            ]
        }

        # Parametri usati per efettuare la get 
        params = {
            "filters": json.dumps(filters),
            # Altri campi per ottenere maggiori informazioni sui file scaricati 
            "fields": "file_name,file_size,created_datetime,updated_datetime,data_type,experimental_strategy,data_category,cases.project.project_id,cases.case_id,cases.submitter_id,associated_entities.entity_submitter_id",
            "format": "JSON",
            "size": "600",  # Numero massimo di file da scaricare per richiesta
            "pretty": "true"  # pretty indica che la response viene formattata con spazi aggiuntivi per migliorare la leggibilità
        }
        
        response = requests.get(gdc_api_url, params=params)


        # Elaborazione dei dati e inserimento nel database
        for file_info in json.loads(response.content.decode("utf-8"))["data"]["hits"]:
            
            file_id = file_info["id"]
            print(file_id)
            # Gestione dei progetti 
            project_id = file_info["cases"][0]["project"]["project_id"]
            # Controllo se il progetto esiste già nel database 
            if not checkExistProject(project_id, cursor): 
                project_name = searchProject(project_id)
                # Se ho recuperato informazioni sul progetto allora faccio l'insert nel database 
                if project_name != None:
                    insertNewProject(project_id, project_name, cursor, conn)
                    conn.commit()

            # Gestione dei case
            if not checkExistCase(file_info["cases"][0]["submitter_id"], cursor):
                case_data = searchCase(file_info["cases"][0]["case_id"])
                if case_data != None:
                    insertNewCase(case_data, project_id, cursor, conn)
                    conn.commit()


            type_id = None

            # Gestione dei file 
            if not checkExistFile(file_id, cursor):
                type_id = insertNewAnalysis(file_id, file_info, project_id, cursor, conn)
                conn.commit()
                expression_data = downloadFile(file_id, type_id)
                if expression_data == None:
                    return 
                

                # !!!! 

                
                # MANCA UN DOPPIO TRY EXCEPT CHE COPRE IL CONTENUTO DI QUESTA FUNZIONE: UNO PER GLI ERRORI DEL DB E UNO PER GLI ERRORI GENERICI

                for entity in file_info["associated_entities"]: 
                        if checkExistBiospecimen(entity["entity_submitter_id"], cursor):
                            cursor.execute("INSERT INTO analysis_entity VALUES (%s, %s)", (file_id, entity["entity_submitter_id"]))
                conn.commit()
                if type_id == 1:
                        for data_row in expression_data:
                            # Inserimento dei dati di espressioni GENICHE nel database
                            gene_id = data_row["gene_id"]
                            stranded_first = data_row["stranded_first"]
                            stranded_second = data_row["stranded_second"]

                            gene_type_id = getGeneType(data_row["gene_type"], cursor, conn)

                            # Inserisci il gene nel database
                            cursor.execute("INSERT INTO gene VALUES (%s, %s, %s) ON CONFLICT (gene_id) DO NOTHING;", (gene_id, data_row["gene_name"], gene_type_id))

                            if stranded_first != 0 and stranded_second != 0: 
                                cursor.execute("INSERT INTO gene_expression_file VALUES (%s, %s, %s, %s, %s, %s, %s, %s)", (file_id, gene_id, data_row["tpm_unstranded"], data_row["fpkm_unstranded"], data_row["fpkm_uq_unstranded"], data_row["unstranded"], stranded_first, stranded_second))
                        conn.commit()
                elif type_id == 2:
                        # Inserimento dei dati di espressioni PROTEICHE nel database
                        for data_row in expression_data:
                            agid = data_row["AGID"]
                            expression = data_row["protein_expression"]

                            # Inserisci la proteina nel database
                            cursor.execute("INSERT INTO protein VALUES (%s, %s, %s, %s, %s) ON CONFLICT (agid) DO NOTHING;", (agid, data_row["lab_id"], data_row["catalog_number"], data_row["set_id"], data_row["peptide_target"]))
                            
                            if expression != "NaN": cursor.execute("INSERT INTO protein_expression_file VALUES (%s, %s, %s)", (file_id, agid, expression))
                        conn.commit()
                print("File inserito nel database")
            else: 
                #print("Il file è gia presente nel database")
                pass
            conn.commit()

        print(f"Download, elaborazione e inserimento dei dati completati.")

'''
    except Exception as error:
        # Gestione generica degli errori
        conn.rollback()
        print(f"Errore sconosciuto: {error}")

    finally:
        # Ripristina l'autocommit
        conn.autocommit = True

        # Chiudi la connessione
        cursor.close()
        conn.close()
    '''


'''
Funzione che ricerca i dati di un singolo progetto
'''
def searchProject(id):
    project_url = "https://api.gdc.cancer.gov/projects/" + id
    params = {
        #Puoi aggiungere altri campi che danno più info relative al progetto
        "fields": "name",
        "format": "JSON",
        "pretty": "true"
    }
    response = requests.get(project_url, params=params)

    if response.status_code == 200:
        data = json.loads(response.content.decode("utf-8"))["data"]
        return data["name"]
    else:
        print(f"Errore durante il download del progetto: {response.status_code}")
        return None

'''
Funzione che ricerca i dati di un singolo case
'''
def searchCase(id):
    cases_url = "https://api.gdc.cancer.gov/cases/" + id

    params = {
        #Puoi aggiungere altri campi che danno più info relative al caso
        "fields": "submitter_id,demographic.ethnicity,demographic.gender,demographic.race,demographic.vital_status,primary_site,disease_type,samples.submitter_id,samples.sample_type,samples.sample_type_id,samples.tumor_code,samples.tumor_code_id,samples.tumor_descriptor,samples.portions.submitter_id,samples.portions.analytes.submitter_id,samples.portions.analytes.concentration,samples.portions.analytes.aliquots.submitter_id,samples.portions.analytes.aliquots.concentration", #samples.portions.slides.submitter_id
        "format": "JSON",
        "pretty": "true"
    }
    response = requests.get(cases_url, params=params)

    if response.status_code == 200:
        data = json.loads(response.content.decode("utf-8"))["data"]
        return data
    
    print(f"Errore durante il download del case: {response.status_code}")
    return None 

'''
Funzione che inserisce i dati di un singolo nuovo case all'interno del database
'''
def insertNewCase(data, project_id, cursor, conn):
    #search_site_malattia = "SELECT site_id, disease_id FROM primary_site, disease WHERE LOWER(site) = LOWER('{}') AND LOWER(type) = LOWER('{}')"
    insert_case = "INSERT INTO public.case VALUES ('{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}');"

    primary_site = getPrimarySite(data["primary_site"], cursor, conn)
    disease = getDisease(data["disease_type"], cursor,conn)

    if "disease_type" in data:        
        cursor.execute(insert_case.format(data["submitter_id"], data["demographic"]["ethnicity"], data["demographic"]["gender"], data["demographic"]["race"], data["demographic"]["vital_status"], project_id, primary_site , disease))
        insertNewSamples(data["samples"], data["submitter_id"], cursor, conn)

'''
Funzione che inserisce i dati dei nuovi campioni all'interno del database
'''
def insertNewSamples(samples, case_id, cursor,conn):
    inserisci_biospecie = "INSERT INTO biospecimen VALUES (%s, %s, %s)"
    inserisci_tumore = "INSERT INTO tumor VALUES (%s, %s, %s) ON CONFLICT (tumor_code_id) DO NOTHING;"
    inserisci_tipo_campione = "INSERT INTO sample_type VALUES (%s, %s) ON CONFLICT (type_id) DO NOTHING;"
    inserisci_campione = "INSERT INTO sample VALUES (%s, %s, %s)"
    inserisci_porzione = "INSERT INTO portion VALUES (%s, %s)"
    inserisci_analita = "INSERT INTO analyte VALUES (%s, %s, %s)"
    inserisci_aliquota = "INSERT INTO aliquote VALUES (%s, %s, %s)"

    for sample in samples:
        sample_id = sample["submitter_id"]
        
        if "tumor_code_id" in sample and sample["tumor_code_id"] != None: 
            tumor_code = sample["tumor_code_id"]
            cursor.execute(inserisci_tumore, (tumor_code, sample["tumor_code"], sample["tumor_descriptor"]))
        else: tumor_code = None
        if "sample_type_id" in sample and sample["sample_type_id"] != None: 
            type_id = sample["sample_type_id"]
            cursor.execute(inserisci_tipo_campione, (type_id, sample["sample_type"]))
        else: type_id = None   


        cursor.execute(inserisci_biospecie, (sample_id, case_id, 1))
        cursor.execute(inserisci_campione, (sample_id, type_id, tumor_code))
        if "portions" in sample:
            for portion in sample["portions"]:
                try:
                    portion_id = portion["submitter_id"]

                    cursor.execute(inserisci_biospecie, (portion_id, case_id, 2))
                    cursor.execute(inserisci_porzione, (portion_id, sample_id))
                    if "analytes" in portion:
                        for analyte in portion["analytes"]:
                            analyte_id = analyte["submitter_id"]

                            cursor.execute(inserisci_biospecie, (analyte_id, case_id, 3))
                            cursor.execute(inserisci_analita, (analyte_id, portion_id, analyte["concentration"]))
                            if "aliquots" in analyte:
                                for aliquote in analyte["aliquots"]:
                                    aliquote_id = aliquote["submitter_id"]

                                    cursor.execute(inserisci_biospecie, (aliquote_id, case_id, 4))
                                    cursor.execute(inserisci_aliquota, (aliquote_id, analyte_id, aliquote["concentration"]))
                except:
                    pass

'''
Funzione che inserisce i dati di un singolo nuovo file all'interno del database
'''
def insertNewAnalysis(file_id, file_info, project_id, cursor, conn):
    dataType = getDataType(file_info["data_type"], cursor, conn)
    dataCategory = getDataCategory(file_info["data_category"], cursor, conn)
    expStrategy = getExperimentalStrategy(file_info["experimental_strategy"], cursor, conn)

    # Inserisci i dettagli del file nel database
    cursor.execute("INSERT INTO analysis VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)", (file_id, file_info["file_name"], file_info["file_size"], file_info["created_datetime"], file_info["updated_datetime"], project_id, dataType, dataCategory, expStrategy))
    return dataType

'''
Funzione per il download di un singolo file 
'''
def downloadFile(file_id, type_id):

    file_url = "https://api.gdc.cancer.gov/data/" + file_id
    response = requests.get(file_url)

    if response.status_code == 200:
        # Elabora i dati dal file scaricato
        if type_id == 1: 
            data = pd.read_csv(StringIO(response.text), sep="\t", comment="#", skiprows=[2,3,4,5])
        elif type_id == 2: 
            data = pd.read_csv(StringIO(response.text), sep="\t", comment="#")
    
        # Trasforma i dati in una lista di dizionari
        expression_data = data.to_dict(orient="records")

        return expression_data
    else:
        print(f"Errore durante il download del file: {response.status_code}")
        return None

'''
cursor,conn = databaseConnection()
if cursor == None:
    print("Errore nello stabilire la connessione col server")
    sys.exit()

print("CONNESSIONE AL DATABASE STABILITA")

'''


# SE IL DB NON ESISTE E SI LANCIA DIRETTAMENTE QUESTA FUNZIONE, ALLA PRIMA INSERT ANDRA' IN ERRORE PERCHE' NON TROVERA' I DATI -> VALUTARE SE E' NECESSARIO CREARE UNA NUOVA CONNESSIONE COL DB E POI PROCEDERE 
download_and_process_expression_data(params)