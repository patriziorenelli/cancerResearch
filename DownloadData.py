from DatabaseManager import *
import params 
import sys
import requests
import psycopg2
import json
import csv



# Funzione per scaricare e processare i dati di espressione da GDC
'''
Gli passo params in modo da potervi accedere 
'''
def download_and_process_expression_data(param):

        # Creo connessione con il database 
        cursor, conn = databaseConnection()
        if cursor == None or conn == None:
            print("Impossibile connettersi al database")
            return 
        else: 
            print("Connessione riuscita")

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
            "size": "20",  # Numero massimo di file da scaricare per richiesta
            "pretty": "true"  # pretty indica che la response viene formattata con spazi aggiuntivi per migliorare la leggibilità
        }
        
        response = requests.get(gdc_api_url, params=params)
        data = response.json()

        # Elaborazione dei dati e inserimento nel database
        for file_info in json.loads(response.content.decode("utf-8"))["data"]["hits"]:

            file_id = file_info["id"]

            # Gestione dei progetti 
            project_id = file_info["cases"][0]["project"]["project_id"]
            # Controllo se il progetto esiste già nel database 
            if not checkExistProject(project_id, cursor): 
                project_name = searchProject(project_id)
                # Se ho recuperato informazioni sul progetto allora faccio l'insert nel database 
                if project_name != None:
                    insertNewProject(project_id, project_name, cursor, conn)

            # Gestione dei case
            if not checkExistCase(file_info["cases"][0]["submitter_id"], cursor):
                case_data = searchCase(file_info["cases"][0]["case_id"])
                if case_data != None:
                    insertNewCase(case_data, project_id, cursor, conn)


            type_id = None
            # Gestione dei file 
            if not checkExistFile(file_id, cursor):
                type_id = insertNewAnalysis(file_id, file_info, project_id, cursor, conn)

            

                expression_data = downloadFile(file_id, type_id)
                if expression_data == None:
                    return 
                

                # FIN QUI TUTTO OK  


                # VEDERE COME CAMBIARE QUESTA PARTE SOTTO E LA FUNZIONE  insertNewSamples
                # MANCA UN DOPPIO TRY EXCEPT CHE COPRE IL CONTENUTO DI QUESTA FUNZIONE: UNO PER GLI ERRORI DEL DB E UNO PER GLI ERRORI GENERICI  -> COME HA FATTO VALERIO 

# SELECT COUNT(*) FROM gene_expression_file -> 582308

                for entity in file_info["associated_entities"]: 
                        cursor.execute("INSERT INTO analysis_entity VALUES (%s, %s)", (file_id, entity["entity_submitter_id"]))
                conn.commit()
                    
                if type_id == 1:
                        for data_row in expression_data:
                            # Inserimento dei dati di espressioni GENICHE nel database
                            gene_id = data_row["gene_id"]
                            stranded_first = data_row["stranded_first"]
                            stranded_second = data_row["stranded_second"]

                            cursor.execute("SELECT type_id FROM gene_type WHERE type = %s", (data_row["gene_type"],))
                            gene_type_id = cursor.fetchone()[0]

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
                print("Il file è gia presente nel database")

        print(f"Download, elaborazione e inserimento dei dati completati.")



'''
Verifica se esiste un progetto all'interno del database
'''
def checkExistProject(id, cursor):
    cursor.execute("SELECT COUNT(*) FROM project WHERE project_id = %s", (id,))
    result = cursor.fetchone()
    if result[0] == 0: 
        return False
    return True

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
Funzione che inserisce i dati di un singolo nuovo progetto all'interno del database
'''
def insertNewProject(id, name, cursor,conn):
    query = "INSERT INTO public.project VALUES ('{}', '{}') ON CONFLICT (project_id) DO NOTHING;".format(id,name)
    cursor.execute(query)
    conn.commit()

'''
Verifica se esiste un caso all'interno del database
'''
def checkExistCase(id, cursor):
    cursor.execute("SELECT COUNT(*) FROM public.case WHERE case_id = %s", (id,))
    result = cursor.fetchone()
    if result[0] == 0: 
        return False
    return True

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
    search_site_malattia = "SELECT site_id, disease_id FROM primary_site, disease WHERE LOWER(site) = LOWER('{}') AND LOWER(type) = LOWER('{}')"
    insert_case = "INSERT INTO public.case VALUES ('{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}');"
    
    cursor.execute(search_site_malattia.format(data["primary_site"], data["disease_type"],))
    disease_site = cursor.fetchone()

    cursor.execute(insert_case.format(data["submitter_id"], data["demographic"]["ethnicity"], data["demographic"]["gender"], data["demographic"]["race"], data["demographic"]["vital_status"], project_id, disease_site[0], disease_site[1]))
    conn.commit()
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
    conn.commit()

'''
Verifica se esiste un file all'interno del database
'''
def checkExistFile(id, cursor):
    cursor.execute("SELECT COUNT(*) FROM analysis WHERE file_id = %s", (id,))
    result = cursor.fetchone()
    if result[0] == 0: 
        return False
    return True

'''
Funzione che inserisce i dati di un singolo nuovo file all'interno del database
'''
def insertNewAnalysis(file_id, file_info, project_id, cursor, conn):
    cursor.execute("SELECT type_id, category_id, strategy_id FROM data_type, data_category, experimental_strategy WHERE type = %s AND category = %s AND strategy = %s", (file_info["data_type"], file_info["data_category"], file_info["experimental_strategy"],))
    type_category_strategy_id = cursor.fetchone()
    type_id = type_category_strategy_id[0]

    # Inserisci i dettagli del file nel database
    cursor.execute("INSERT INTO analysis VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)", (file_id, file_info["file_name"], file_info["file_size"], file_info["created_datetime"], file_info["updated_datetime"], project_id, type_id, type_category_strategy_id[1], type_category_strategy_id[2]))
    conn.commit()           
    return type_id


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
download_and_process_expression_data(params)