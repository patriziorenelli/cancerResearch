from DatabaseManager import *
import params 
import sys
import requests
import psycopg2
import json
import csv





#  I dati su PDC girano intorno ai singoli studi, organizzando i dati in studi basati su su caratteristiche come proteoma o PTM e tipi sperimentali come senza etichetta o TMT 
# In genere gli studi sono specifici per la malattia e per la sede primitiva -> primary site -> IN PROJECT METTERE GLI STUDY 

# FARE ATTENZIONE AGLI OFFSET E LIMIT DELLE SINGOLE API CHE SONO CAMPI OBBLIGATORI PER QUASI TUTTE 

class Program:
    def __init__(self, program_id, program_submitter_id, program_name, projects):
        self.program_id = program_id
        self.program_submitter_id = program_submitter_id
        self.program_name = program_name
        self.projects = projects    # è un array

class Project:
   def __init__(self,  project_id, project_submitter_id, project_name, studies):
    self. project_id =  project_id
    self.project_submitter_id = project_submitter_id
    self.project_name = project_name
    self.studies = studies  # è un array
    

class Study:
    def __init__(self, study_id, study_submitter_id, study_name, disease_types, primary_sites):
        self.study_id = study_id
        self.study_submitter_id = study_submitter_id
        self.study_name = study_name
        self.disease_types = disease_types  # è un array
        self.primary_sites = primary_sites  # è un array

'''
Funzione che ottiene i dati di tutti gli studi, programmi e progetti disponibili, necessari per ottenere tutti gli altri dati disponibili 
'''
def getPrograms():


    gdc_api_url = "https://pdc.cancer.gov/graphql?query={allPrograms (acceptDUA: true)  {program_id  program_submitter_id  name projects  {project_id  project_submitter_id  name  studies  {pdc_study_id study_id study_submitter_id submitter_id_name analytical_fraction study_name disease_types primary_sites embargo_date experiment_type acquisition_type} }}}"
    response = requests.get(gdc_api_url)

    # FORSE BISOGNA FARE DIVERSE VOLTE LA QUERY E SALVARE IN STATUS I DATI PER RECUPERARE POI L'OFFSET DELLE QUERY

    programs = []
        
    prog = json.loads(response.content.decode("utf-8"))

    if "data" not in prog and "allPrograms" not in prog["data"]:
        return 


    # Da qui possiamo prendere i programmi == project e tutti i studi associati ad ogni programma 
    for program in prog["data"]["allPrograms"]:
        studies = []
        projects = []
        if "projects" not in program:
            break
        for pr in program["projects"]:
            if "studies" not in pr:
                break 
            for st in pr["studies"]:
                # Qui si puo' applicare il filtro sul primary_site che è relativo ai study 
                if "study_id" not in st or "study_submitter_id" not in st or "study_name" not in st or "disease_types" not in st or "primary_sites" not in st:
                    break 
                studies.append(Study(st["study_id"], st["study_submitter_id"], st["study_name"], st["disease_types"],st["primary_sites"] ))
            if "project_id" not in pr or "project_submitter_id" not in pr or "name" not in pr:                
                break
            projects.append(Project(pr["project_id"], pr["project_submitter_id"], pr["name"], studies))
            if "program_id" not in program or "program_submitter_id" not in program or "name" not in program:
                break
        programs.append( Program(program["program_id"], program["program_submitter_id"],program["name"], projects ) )

    return programs

# GENE PRESENTE SIA IN PDC CHE IN GDC select * from gene, gene_type where  name = 'A1BG'and gene.type = type_id


# FARE SAVE DEI STUDY ALL'INTERNO DELLA TABELLA PROJECT 
'''
Funzione che ottiene i case relativi ad un singolo programma
'''
def getCases(study):
    cases = []

    # Otteniamo il numero di cases relativi allo studio
    gdc_api_url = 'https://pdc.cancer.gov/graphql?query={paginatedCaseDemographicsPerStudy (study_id: "' + study +  '" offset: 0 limit: 1 acceptDUA: true) { total caseDemographicsPerStudy { case_id case_submitter_id disease_type primary_site demographics { demographic_id ethnicity gender demographic_submitter_id race cause_of_death days_to_birth days_to_death vital_status year_of_birth year_of_death age_at_index premature_at_birth weeks_gestation_at_birth age_is_obfuscated cause_of_death_source occupation_duration_years country_of_residence_at_enrollment} } pagination { count sort from page total pages size } }}'
    response = requests.get(gdc_api_url)
    cases_number = json.loads(response.content.decode("utf-8"))

    if "data" not in cases_number or "paginatedCaseDemographicsPerStudy" not in cases_number["data"] or "total" not in cases_number["data"]["paginatedCaseDemographicsPerStudy"]:
        return 
    cases_number = str( json.loads(response.content.decode("utf-8"))["data"]["paginatedCaseDemographicsPerStudy"]["total"] )
    #print(json.loads(response.content.decode("utf-8"))["data"])

    # FORSE BISOGNA RIPETERE DIVERSE VOLTE LA QUERY

    # Otteniamo i cases relativi allo studio 
    gdc_api_url = 'https://pdc.cancer.gov/graphql?query={paginatedCaseDemographicsPerStudy (study_id: "' + study +  '" offset: 0 limit: ' + cases_number + ' acceptDUA: true) { total caseDemographicsPerStudy { case_id case_submitter_id disease_type primary_site demographics { demographic_id ethnicity gender demographic_submitter_id race cause_of_death days_to_birth days_to_death vital_status year_of_birth year_of_death age_at_index premature_at_birth weeks_gestation_at_birth age_is_obfuscated cause_of_death_source occupation_duration_years country_of_residence_at_enrollment} } pagination { count sort from page total pages size } }}'
    response = requests.get(gdc_api_url)
    re = json.loads(response.content.decode("utf-8"))
    if "data" not in re or "paginatedCaseDemographicsPerStudy" not in re["data"] or "total" not in re["data"]["paginatedCaseDemographicsPerStudy"]:
        return

    for case in json.loads(response.content.decode("utf-8"))["data"]["paginatedCaseDemographicsPerStudy"]["caseDemographicsPerStudy"]:
        #print(case)
        # FARE CHECK SU DISEASE NEL DB E EVENTUALE INSERT 
        # QUI PRENDERE L'ID DEL PRIMARY SITE E DEL DISEASE SE SONO GIA' INSERITI NELLA TABELLA SE NO FACCIAMO INSERT ( FUNZIONI PRESENTI NEL DatabaseGenericInteraction )
        # FARE INSERT DEL SINGOLO CASE 
        pass 

    return cases

def getSample(study):
    # CONNESSIONE COL DB 
    cursor, conn = databaseConnection()

    #print(study)
    gdc_api_url = 'https://pdc.cancer.gov/graphql?query={ paginatedCasesSamplesAliquots(study_id:"' + study +  '"  offset:0 limit: 1 acceptDUA: true) { total casesSamplesAliquots { case_id case_submitter_id days_to_lost_to_followup disease_type index_date lost_to_followup primary_site samples { sample_id sample_submitter_id sample_type sample_type_id gdc_sample_id gdc_project_id biospecimen_anatomic_site composition current_weight days_to_collection days_to_sample_procurement diagnosis_pathologically_confirmed freezing_method initial_weight intermediate_dimension longest_dimension method_of_sample_procurement pathology_report_uuid preservation_method sample_type_id shortest_dimension time_between_clamping_and_freezing time_between_excision_and_freezing tissue_type tumor_code tumor_code_id tumor_descriptor diagnoses{ diagnosis_id diagnosis_submitter_id annotation} aliquots { aliquot_id aliquot_submitter_id analyte_type aliquot_run_metadata { aliquot_run_metadata_id label experiment_number fraction replicate_number date alias analyte} } } } pagination { count sort from page total pages size } } }'
    response = requests.get(gdc_api_url)
    samples_number = str( json.loads(response.content.decode("utf-8"))["data"]["paginatedCasesSamplesAliquots"]["total"] )


    gdc_api_url = 'https://pdc.cancer.gov/graphql?query={ paginatedCasesSamplesAliquots(study_id:"' + study +  '"  offset:0 limit: ' + samples_number + ' acceptDUA: true) { total casesSamplesAliquots { case_id case_submitter_id days_to_lost_to_followup disease_type index_date lost_to_followup primary_site samples { sample_id sample_submitter_id sample_type sample_type_id gdc_sample_id gdc_project_id biospecimen_anatomic_site composition current_weight days_to_collection days_to_sample_procurement diagnosis_pathologically_confirmed freezing_method initial_weight intermediate_dimension longest_dimension method_of_sample_procurement pathology_report_uuid preservation_method sample_type_id shortest_dimension time_between_clamping_and_freezing time_between_excision_and_freezing tissue_type tumor_code tumor_code_id tumor_descriptor diagnoses{ diagnosis_id diagnosis_submitter_id annotation} aliquots { concentration aliquot_id aliquot_submitter_id analyte_type concentration aliquot_run_metadata { aliquot_run_metadata_id label experiment_number fraction replicate_number date alias analyte} } } } pagination { count sort from page total pages size } } }'
    response = requests.get(gdc_api_url)
    #print(json.loads(response.content.decode("utf-8")))

    for samples in json.loads(response.content.decode("utf-8"))["data"]["paginatedCasesSamplesAliquots"]["casesSamplesAliquots"]:
        case_submitter_id = samples['case_submitter_id']
        for sample in samples["samples"]:
            #print(sample)


            tumor_code = sample['tumor_code']
            tumor_code_id = sample['tumor_code_id']
            tumor_description = sample['tumor_descriptor']
            # fare insert tumor 
            #   inserisci_tumore = "INSERT INTO tumor VALUES (%s, %s, %s) ON CONFLICT (tumor_code_id) DO NOTHING;"
            #   cursor.execute(inserisci_tumore, (tumor_code, sample["tumor_code"], sample["tumor_descriptor"]))

            sample_type = sample['sample_type']
            sample_type_id = sample['sample_type_id']

            #print( str(sample_type_id) + " "+ str(sample_type))

            if sample_type_id == None:
                q = "SELECT type_id FROM sample_type WHERE LOWER(type) = LOWER('{}')"
                cursor.execute(q.format(sample_type))
                sample_type_id =  cursor.fetchone()
                sample_type_id = sample_type_id
                if sample_type_id == None:
                        continue
                else:
                    sample_type_id = sample_type_id[0] 
                    # fare insert usando sample_type_id
            else:
                # fare insert su sample_type con la cosa conflict
                pass

            # sample['sample_submitter_id'] può essere un'array quindi bisogna fare uno split su , e fare l'insert poer i singoli samp in sample['sample_submitter_id]
            for samp in sample['sample_submitter_id'].split(','):
                sample_id =  samp
                # fare insert sample 
                # con fk sul tumor usare tumor_code_id
                # con fk sul type usare sample_type_id


                #print("\n")
                # fai insert su biospecimen con id = sample_id e  case_submitter_id ed type = 1 
                for aliquote in sample['aliquots']:
                    concentration = aliquote['concentration']
                    aliquote_id = aliquote['aliquot_submitter_id']
                    # fai insert su biospecimen con aliquote_id e case = sample_id ed type= 4 
                    # fai insert su aliquote con primary key = aliquote_id (IN PDC NON ABBIAMO UN ANALYTE_ID)  analyte_id = aliquote_id  e concentration  
                #print(case_submitter_id,sample_id ,aliquote_id)


def getGenes():

    # QUI BISOGNA CONSIDERARE L'OFFSET E I LIMIT DAL FILE status.txt
    gdc_api_url = 'https://pdc.cancer.gov/graphql?query={ getPaginatedGenes(offset: 0 limit: 100 acceptDUA: true) { total genesProper { gene_id gene_name NCBI_gene_id authority description organism chromosome locus proteins assays } pagination { count sort from page total pages size } } }'
    response = requests.get(gdc_api_url)
    re = json.loads(response.content.decode("utf-8"))

    if "data" not in re or "getPaginatedGenes" not in re["data"] or "genesProper" not in re["data"]["getPaginatedGenes"]:
        return 

    for gene in  json.loads(response.content.decode("utf-8"))["data"]["getPaginatedGenes"]["genesProper"]:
        gene_name = gene["gene_name"]
        gdc_api_url= 'https://pdc.cancer.gov/graphql?query={geneSpectralCount (gene_name: "' + gene_name+ '" acceptDUA: true){gene_id gene_name NCBI_gene_id authority description organism chromosome locus proteins assays spectral_counts { project_submitter_id plex spectral_count distinct_peptide unshared_peptide study_submitter_id} }}'
        response = requests.get(gdc_api_url)
        re = json.loads(response.content.decode("utf-8"))
        if "data" not in re or "geneSpectralCount" not in re["data"]:
            break
        
        geneSpectralCount = re["data"]["geneSpectralCount"]

        #  QUI OPERAZIONI SUI GENI 

# ---------   TEST --------------------
        
        # FARE RICHIESTA CON NUOVA API INDIVIDUATA E PRENDERE TUTTI I DATI 
        #gdc_api_url = 'http://rest.ensembl.org/lookup/symbol/homo_sapiens/' + 'ASMTL' + '?content-type=application/json'
        #dati_gene_ens = json.loads(requests.get(gdc_api_url).content.decode("utf-8"))

        #print(dati_gene_ens)

    
        # https://www.ncbi.nlm.nih.gov/datasets/docs/v2/reference-docs/rest-api/#post-/gene

        # VEDERE SE E' POSSIBILE PRENDER INFORMAZIONI ANCHE SULLE PROTEINE 





# ---------------- FINE TEST -------------------



        gene_id = "ID"
        # INSERT IN GENE usare gene_id, gene_name, type = DA PRENDERE NELL'API SOPRA DA FARE   E AGGIORNARE IL FILE status.txt

        for genSpec in geneSpectralCount:
            if "spectral_counts" not in genSpec or "proteins" not in genSpec:
                break

            proteins = (genSpec["proteins"]).split(";")
            spectral_counts = genSpec["spectral_counts"]

            for spec in spectral_counts:
                if "study_submitter_id" not in spec or "spectral_count" not in spec or "distinct_peptide" not in spec or "unshared_peptide" not in spec:
                   break 
                study_submitter_id = spec["study_submitter_id"]
                spectral_count = spec["spectral_count"]
                distinct_peptide = spec["distinct_peptide"]
                unshared_peptide = spec["unshared_peptide"]
                # QUI FACCIAMO INSERT SULLA NUOVA TABELLA 
    pass


def sviluppo():            
    programmi = getPrograms()
    #print(len(programmi))
    for programma in programmi:
        #print("PROGRAMMA: "+ programma.program_name + " ID: " + str(programma.program_id))
        for progetto in programma.projects:
            #print(" PROGETTO: " + progetto.project_name + " ID: " + str(progetto.project_id) )
            for studio in progetto.studies: 
                #print("     STUDIO: "+ studio.study_name + " ID: " + str(studio.study_id))

                # QUI BISOGNA FARE INSERT PER LO STUDIO NELLA TABELLA PROJECT E DAL PRIMARY SITE DEL PROJECT FARE INSERT NELLA TABELLA PRIMARY_SITE
                #getCases(studio.study_id)
                #getSample(studio.study_id)

                getGenes()

                #print(studio.disease_types)




'''
QUERY DA VEDERE PER ANALYSIS
select file_id, filename, file_size, created_datetime,updated_datetime, project, category, experimental_strategy.strategy_id, type
from analysis join data_category on data_category.category_id = data_category 
			  join  data_type on data_type.type_id = data_type
			  join experimental_strategy on experimental_strategy.strategy_id = experimental_strategy
'''

sviluppo()



