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


'''
    Esempio di response ottenuto 
{'data': {'hits': [
    {'id': '6feef177-114c-4285-b242-481fe0aea551', 'cases': 
        [{'case_id': 'aee86a89-0377-4080-b16c-408bfbe78687', 'submitter_id': 'TCGA-69-7980', 'project': {'project_id': 'TCGA-LUAD'}}], 
        'associated_entities': [{'entity_submitter_id': 'TCGA-69-7980-01A-11R-2187-07'}], 
        'file_name': '77322072-2a7f-49e6-a9d1-c521c25acd70.rna_seq.augmented_star_gene_counts.tsv', 'updated_datetime': '2022-01-19T14:20:39.180245-06:00', 'data_type': 'Gene Expression Quantification', 'data_category': 'Transcriptome Profiling', 'experimental_strategy': 'RNA-Seq', 'file_size': 4257905, 'created_datetime': '2021-12-13T19:35:41.947012-06:00'},
    {'id': 'b9ac77d6-9a1b-443d-8ef5-e8ef2e3008dd', 'cases': 
        [{'case_id': 'a41c46da-7ed4-4192-bd16-b3cbb94a5133', 'submitter_id': 'TCGA-55-1592', 'project': {'project_id': 'TCGA-LUAD'}}], 
        'associated_entities': [{'entity_submitter_id': 'TCGA-55-1592-01A-01R-0946-07'}], 'file_name': '6f6bf240-1ca4-47d0-9a77-17b0ce9b8ae7.rna_seq.augmented_star_gene_counts.tsv', 'updated_datetime': '2022-01-19T14:21:07.893105-06:00', 'data_type': 'Gene Expression Quantification', 'data_category': 'Transcriptome Profiling', 'experimental_strategy': 'RNA-Seq', 'file_size': 4264851, 'created_datetime': '2021-12-13T19:55:53.312203-06:00'},
    {'id': '3563bce2-6547-4081-883e-1e7e498c83be', 'cases': [{'case_id': 'ba49117e-dab6-4e7d-bc44-f11dcafa1318', 'submitter_id': 'TCGA-55-7727', 'project': {'project_id': 'TCGA-LUAD'}}], 
        'associated_entities': [{'entity_submitter_id': 'TCGA-55-7727-01A-11R-2170-07'}], 'file_name': '59e8b7b7-5183-4655-aa5e-e4b5ba73eded.rna_seq.augmented_star_gene_counts.tsv', 'updated_datetime': '2022-01-19T14:20:16.513483-06:00', 'data_type': 'Gene Expression Quantification', 'data_category': 'Transcriptome Profiling', 'experimental_strategy': 'RNA-Seq', 'file_size': 4217198, 'created_datetime': '2021-12-13T20:00:15.260272-06:00'}, 
    {'id': '68b00cb6-4335-4c64-a3e0-0c29ed574480', 'cases': [{'case_id': 'c4d1e105-28b7-48df-abef-fbe09782fdb2', 'submitter_id': 'TCGA-55-6972', 'project': {'project_id': 'TCGA-LUAD'}}], 
        'associated_entities': [{'entity_submitter_id': 'TCGA-55-6972-01A-11R-1949-07'}], 'file_name': '5418228b-cfd0-4580-87c6-3ebf6282ad73.rna_seq.augmented_star_gene_counts.tsv', 'updated_datetime': '2022-01-19T14:20:37.428774-06:00', 'data_type': 'Gene Expression Quantification', 'data_category': 'Transcriptome Profiling', 'experimental_strategy': 'RNA-Seq', 'file_size': 4211769, 'created_datetime': '2021-12-13T19:48:35.287560-06:00'}, 
    {'id': '55831884-c907-457d-bb2c-7c7b3f7c4cd1', 'cases': [{'case_id': 'bab43415-d413-40be-a4c0-2c40a52afe6a', 'submitter_id': 'TCGA-44-2668', 'project': {'project_id': 'TCGA-LUAD'}}], 
        'associated_entities': [{'entity_submitter_id': 'TCGA-44-2668-11A-01R-1758-07'}], 'file_name': 'c7fd0bf8-753e-45d6-b987-51ec7559f728.rna_seq.augmented_star_gene_counts.tsv', 'updated_datetime': '2022-01-19T14:20:30.018854-06:00', 'data_type': 'Gene Expression Quantification', 'data_category': 'Transcriptome Profiling', 'experimental_strategy': 'RNA-Seq', 'file_size': 4237695, 'created_datetime': '2021-12-13T19:51:18.747467-06:00'}, 
    {'id': '4089d037-ab25-47a6-be68-19742473cbc6', 'cases': [{'case_id': 'cd9e70e4-8622-4a07-8646-63f8275c1737', 'submitter_id': 'TCGA-49-AARE', 'project': {'project_id': 'TCGA-LUAD'}}], 
        'associated_entities': [{'entity_submitter_id': 'TCGA-49-AARE-01A-11R-A41B-07'}], 'file_name': '50c308c9-922a-4083-ae09-e5e4d8c437af.rna_seq.augmented_star_gene_counts.tsv', 'updated_datetime': '2022-01-19T14:20:21.969629-06:00', 'data_type': 'Gene Expression Quantification', 'data_category': 'Transcriptome Profiling', 'experimental_strategy': 'RNA-Seq', 'file_size': 4242766, 'created_datetime': '2021-12-13T19:54:03.170411-06:00'}, 
    {'id': 'db0caa6a-e863-4dad-a911-0c69127be9df', 'cases': [{'case_id': 'cc68632c-b1e3-491b-b562-9468e2d1c101', 'submitter_id': 'TCGA-86-7713', 'project': {'project_id': 'TCGA-LUAD'}}],
        'associated_entities': [{'entity_submitter_id': 'TCGA-86-7713-01A-11R-2066-07'}], 'file_name': '55071ef3-bf09-43a2-a54c-a9ec61a84615.rna_seq.augmented_star_gene_counts.tsv', 'updated_datetime': '2022-01-19T14:21:20.189089-06:00', 'data_type': 'Gene Expression Quantification', 'data_category': 'Transcriptome Profiling', 'experimental_strategy': 'RNA-Seq', 'file_size': 4255626, 'created_datetime': '2021-12-13T19:31:57.981047-06:00'},
    {'id': 'a0fce6cc-a525-4970-82b7-8512bb0708b3', 'cases': [{'case_id': 'c9c533ee-e154-4a56-bce9-b5af37574b2f', 'submitter_id': 'TCGA-55-7913', 'project': {'project_id': 'TCGA-LUAD'}}], 
        'associated_entities': [{'entity_submitter_id': 'TCGA-55-7913-01B-11R-2241-07'}], 'file_name': '7d9c7c34-76e0-4622-b5f7-60e12f6d4e07.rna_seq.augmented_star_gene_counts.tsv', 'updated_datetime': '2022-01-19T14:20:58.441948-06:00', 'data_type': 'Gene Expression Quantification', 'data_category': 'Transcriptome Profiling', 'experimental_strategy': 'RNA-Seq', 'file_size': 4252453, 'created_datetime': '2021-12-13T19:51:58.058930-06:00'}, 
    {'id': '38ec487d-0a4a-4287-9c14-4bfdb959b402', 'cases': [{'case_id': 'da345947-498b-4272-a231-a987ed4fe151', 'submitter_id': 'TCGA-44-A47G', 'project': {'project_id': 'TCGA-LUAD'}}],
        'associated_entities': [{'entity_submitter_id': 'TCGA-44-A47G-01A-21R-A24H-07'}], 'file_name': '32675d71-6f79-4b8f-ab7c-e2350b15875c.rna_seq.augmented_star_gene_counts.tsv', 'updated_datetime': '2022-01-19T14:20:18.817877-06:00', 'data_type': 'Gene Expression Quantification', 'data_category': 'Transcriptome Profiling', 'experimental_strategy': 'RNA-Seq', 'file_size': 4235385, 'created_datetime': '2021-12-13T19:34:10.163354-06:00'}, 
    {'id': '1ab1279d-7ccd-4450-8de8-9987bf6627dd', 'cases': [{'case_id': 'ccda26c1-a6d6-4317-8cf8-8a87e15ce12e', 'submitter_id': 'TCGA-44-2662', 'project': {'project_id': 'TCGA-LUAD'}}], 
        'associated_entities': [{'entity_submitter_id': 'TCGA-44-2662-01B-02R-A277-07'}], 'file_name': '3d11905a-16eb-40b2-a36b-e37dca6359d3.rna_seq.augmented_star_gene_counts.tsv', 'updated_datetime': '2022-01-19T14:20:07.524745-06:00', 'data_type': 'Gene Expression Quantification', 'data_category': 'Transcriptome Profiling', 'experimental_strategy': 'RNA-Seq', 'file_size': 4225469, 'created_datetime': '2021-12-13T19:27:33.340965-06:00'}],
         
'pagination': {'count': 10, 'total': 1997, 'size': 10, 'from': 0, 'sort': '', 'page': 1, 'pages': 200}}, 'warnings': {}}

'''