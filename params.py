# Parametri per la connessione al database PostgreSQL
host = 'localhost'
user = 'postgres'
password = '1234'
database = 'GDC'
port = 5432

#Dizionario necessario per la connessione al database PostgreSQL
db_params = {
    'host': host,    
    'database': database,      
    'user': user,     
    'password': password,     
    'port' :  port          
}

# Definizioni delle query SQL utilizzate nel codice
cerca_progetto = "SELECT COUNT(*) FROM project WHERE project_id = %s"
cerca_caso = "SELECT COUNT(*) FROM public.case WHERE case_id = %s"
cerca_file = "SELECT COUNT(*) FROM analysis WHERE file_id = %s"
cerca_tipo_categoria_strategia = "SELECT type_id, category_id, strategy_id FROM data_type, data_category, experimental_strategy WHERE type = %s AND category = %s AND strategy = %s"
cerca_tipo_gene = "SELECT type_id FROM gene_type WHERE type = %s"

inserisci_analisi = "INSERT INTO analysis VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
inserisci_entita_analisi = "INSERT INTO analysis_entity VALUES (%s, %s)"
inserisci_espressione_genica = "INSERT INTO gene_expression_file VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
inserisci_gene = "INSERT INTO gene VALUES (%s, %s, %s) ON CONFLICT (gene_id) DO NOTHING;"
inserisci_proteina = "INSERT INTO protein VALUES (%s, %s, %s, %s, %s) ON CONFLICT (agid) DO NOTHING;"
inserisci_espressione_proteica = "INSERT INTO protein_expression_file VALUES (%s, %s, %s)"
