from DatabaseManager import *
import requests
import json
from requests_html import *
from DatabaseGenericInteraction import * 
from GetGeneProtInformation import *
from GetLog2GeneAliquot import *
import time 


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
    try:
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
    except:
        print("ERRORE FATALE!")
        return None

'''
Funzione che ottiene i case relativi ad un singolo programma
'''
def getCases(study, study_id, cursor, conn):
    #try:
        # Otteniamo il numero di cases relativi allo studio
        gdc_api_url = 'https://pdc.cancer.gov/graphql?query={paginatedCaseDemographicsPerStudy (study_id: "' + study +  '" offset: 0 limit: 1 acceptDUA: true) { total caseDemographicsPerStudy { case_id case_submitter_id disease_type primary_site demographics { demographic_id ethnicity gender demographic_submitter_id race cause_of_death days_to_birth days_to_death vital_status year_of_birth year_of_death age_at_index premature_at_birth weeks_gestation_at_birth age_is_obfuscated cause_of_death_source occupation_duration_years country_of_residence_at_enrollment} } pagination { count sort from page total pages size } }}'
        response = requests.get(gdc_api_url)

        if response.status_code == 204 or response == None or response.content == None:
            return

        cases_number = json.loads(response.content.decode("utf-8"))
        if "data" not in cases_number or "paginatedCaseDemographicsPerStudy" not in cases_number["data"] or "total" not in cases_number["data"]["paginatedCaseDemographicsPerStudy"]:
            return 
        cases_number = str( json.loads(response.content.decode("utf-8"))["data"]["paginatedCaseDemographicsPerStudy"]["total"] )
        #print(json.loads(response.content.decode("utf-8"))["data"])
        print("case number " + str(cases_number) )
        # Otteniamo i cases relativi allo studio 
        gdc_api_url = 'https://pdc.cancer.gov/graphql?query={paginatedCaseDemographicsPerStudy (study_id: "' + study +  '" offset: 0 limit: ' + cases_number + ' acceptDUA: true) { total caseDemographicsPerStudy { case_id case_submitter_id disease_type primary_site demographics { demographic_id ethnicity gender demographic_submitter_id race cause_of_death days_to_birth days_to_death vital_status year_of_birth year_of_death age_at_index premature_at_birth weeks_gestation_at_birth age_is_obfuscated cause_of_death_source occupation_duration_years country_of_residence_at_enrollment} } pagination { count sort from page total pages size } }}'
        response = requests.get(gdc_api_url)
        re = json.loads(response.content.decode("utf-8"))
        #print(re)
        if "data" not in re or "paginatedCaseDemographicsPerStudy" not in re["data"] or "total" not in re["data"]["paginatedCaseDemographicsPerStudy"]:
            return

        #print(json.loads(response.content.decode("utf-8"))["data"]["paginatedCaseDemographicsPerStudy"]["caseDemographicsPerStudy"])
        for case in json.loads(response.content.decode("utf-8"))["data"]["paginatedCaseDemographicsPerStudy"]["caseDemographicsPerStudy"]:
                try:
                    #print(case['case_submitter_id'])
                    if not checkExistCase(case['case_submitter_id'],cursor):
                        if 'demographics' in case:
                            disease = getDisease(case['disease_type'], cursor, conn)
                            primary_site = getPrimarySite( case['primary_site'], cursor, conn)
                            sub_id = case['case_submitter_id']
                            case = case['demographics'][0]
                            insertNewCase(sub_id, case['ethnicity'], case['gender'], case['race'], case['vital_status'], study_id, primary_site, disease, cursor, conn)
                except:
                    print("AIUTO CHECK ")
                    conn.rollback()
                    continue


    #except:
    #    print("ERRORE! ")
    #    pass

'''
Funzione che ottiene tutti i campioni biologici di un singolo studio
'''
def getSample(study, cursor, conn):


    gdc_api_url = 'https://pdc.cancer.gov/graphql?query={ paginatedCasesSamplesAliquots(study_id:"' + study +  '"  offset:0 limit: 1 acceptDUA: true) { total casesSamplesAliquots { case_id case_submitter_id days_to_lost_to_followup disease_type index_date lost_to_followup primary_site samples { sample_id sample_submitter_id sample_type sample_type_id gdc_sample_id gdc_project_id biospecimen_anatomic_site composition current_weight days_to_collection days_to_sample_procurement diagnosis_pathologically_confirmed freezing_method initial_weight intermediate_dimension longest_dimension method_of_sample_procurement pathology_report_uuid preservation_method sample_type_id shortest_dimension time_between_clamping_and_freezing time_between_excision_and_freezing tissue_type tumor_code tumor_code_id tumor_descriptor diagnoses{ diagnosis_id diagnosis_submitter_id annotation} aliquots { aliquot_id aliquot_submitter_id analyte_type aliquot_run_metadata { aliquot_run_metadata_id label experiment_number fraction replicate_number date alias analyte} } } } pagination { count sort from page total pages size } } }'
    response = requests.get(gdc_api_url)
    samples_number = str( json.loads(response.content.decode("utf-8"))["data"]["paginatedCasesSamplesAliquots"]["total"] )


    gdc_api_url = 'https://pdc.cancer.gov/graphql?query={ paginatedCasesSamplesAliquots(study_id:"' + study +  '"  offset:0 limit: ' + samples_number + ' acceptDUA: true) { total casesSamplesAliquots { case_id case_submitter_id days_to_lost_to_followup disease_type index_date lost_to_followup primary_site samples { sample_id sample_submitter_id sample_type sample_type_id gdc_sample_id gdc_project_id biospecimen_anatomic_site composition current_weight days_to_collection days_to_sample_procurement diagnosis_pathologically_confirmed freezing_method initial_weight intermediate_dimension longest_dimension method_of_sample_procurement pathology_report_uuid preservation_method sample_type_id shortest_dimension time_between_clamping_and_freezing time_between_excision_and_freezing tissue_type tumor_code tumor_code_id tumor_descriptor diagnoses{ diagnosis_id diagnosis_submitter_id annotation} aliquots { concentration aliquot_id aliquot_submitter_id analyte_type concentration aliquot_run_metadata { aliquot_run_metadata_id label experiment_number fraction replicate_number date alias analyte} } } } pagination { count sort from page total pages size } } }'
    response = requests.get(gdc_api_url)
    print("sample number: " + str( samples_number)  )
    
    for samples in json.loads(response.content.decode("utf-8"))["data"]["paginatedCasesSamplesAliquots"]["casesSamplesAliquots"]:
        case_submitter_id = samples['case_submitter_id']
        for sample in samples["samples"]:


                #print(sample)
                tumor_code = sample['tumor_code']
                tumor_code_id =  sample['tumor_code_id']
                tumor_description = sample['tumor_descriptor']

                if  len(str(tumor_code_id)) != 0 and len(str(tumor_code)) != 0 and len(str(tumor_description)) != 0 and  str(tumor_code_id) != 'None' and str(tumor_code_id) != 'null' and not checkExistTumor(tumor_code_id, cursor):
                        insertNewTumor(tumor_code_id, tumor_code, tumor_description, cursor, conn)
                else:
                    tumor_code_id = None


                sample_type_id = sample['sample_type_id']
                sample_type = sample['sample_type']
                
                if sample_type_id == None:
                    sample_type_id = searchSampleTypeId(sample_type, cursor)
                    if sample_type_id == None:
                            continue
                    else:
                        sample_type_id = sample_type_id[0] 


                # Se un sample type non è presente lo salvo all'interno del database
                elif not searchSampleTypeId(sample_type, cursor):
                    #print(sample_type_id, sample_type)
                    #print("--------NON C'E'---------")
                    if len(sample_type_id) > 0:

                        sample_type_id = int(sample_type_id.replace('"',''))
                        #print(sample_type_id)
                        insertNewSampleType(sample_type_id, sample_type, cursor, conn)
                        sample_type_id =  searchSampleTypeId(sample_type, cursor)
                    else:
                        # imposto un sample_type_id = None perchè impostare un qualunque altro valore potrebbe causare poi conflitti con altri sample_type con type_id correttamente impostato
                        sample_type_id =  None

                else:
                    # Effettuo comunque la conversione del sample_type_id nel sample_type_id ottenuto dal database ottenuti attraverso il sample_type
                    # Questa azione è necessaria poichè potrebbero esserci sample_type_id che sono collegati ad un sample_type che è salvato nel database con un altro sample_type_id causando errori nel momento dell'insermento nel database 
                    sample_type_id =  searchSampleTypeId(sample_type, cursor)
                    pass
                
                # sample['sample_submitter_id'] può essere un'array quindi bisogna fare uno split su , e fare l'insert per i singoli samp in sample['sample_submitter_id]
                for samp in sample['sample_submitter_id'].split(','):
                    #print("EILA " + samp)
                    sample_id =  samp
                    #print( sample_id, sample_type_id, tumor_code_id, study)
                    if not checkExistBiospecimen(sample_id, cursor):
                        if checkExistCase(case_submitter_id, cursor):
                            
                            #print(sample_id, sample_type_id, tumor_code_id)
                            insertNewBiospecimen(sample_id, case_submitter_id, 1, cursor, conn)
                            #print(sample_type_id, type(sample_type_id)  )
                            #print(sample_type_id, type(sample_type_id), )
                            insertNewSample(sample_id, sample_type_id, tumor_code_id, cursor, conn)
                            #print(sample_id)
                            for aliquote in sample['aliquots']:
                                concentration = aliquote['concentration']
                                aliquote_id = aliquote['aliquot_submitter_id']
                                #print(sample_id)
                                #print(sample_id, aliquote_id, concentration, str(concentration == None))

                                # In PDC non abbiamo questi dati separati quindi l'unico modo per rispettare i vincoli imposti dal database per la parte di GDC è quella di creare portion e analyte fittizi se no ci basterebbe aliquote
                                insertNewPortion(sample_id, sample_id, cursor, conn)
                                insertNewAnalyte(sample_id, sample_id, concentration, cursor,conn)
                                # SI E' TOLTA LA FK TRA ALIQUOTE E ANALYTE & ALIQUOTE E BIOSPECIMEN ->  PER EFFETTUARE QUESTA MODIFICA, PRIMA SI USAVA SAMPLE_ID ANCHE IN ALIQUOTE AL POSTO DI ALIQUOTE_ID -> bisogna vedere se la funzione di scraping web funziona così
                                insertNewAliquote(aliquote_id, sample_id, concentration, cursor, conn)


'''
Funzione che ottiene i dati dei geni disponibili 
'''
def getGenes(cursor,conn):
    # QUI BISOGNA CONSIDERARE L'OFFSET E I LIMIT DAL FILE status.txt
    gdc_api_url = 'https://pdc.cancer.gov/graphql?query={ getPaginatedGenes(offset: 0 limit: 1000 acceptDUA: true) { total genesProper { gene_id gene_name NCBI_gene_id authority description organism chromosome locus proteins assays } pagination { count sort from page total pages size } } }'
    response = requests.get(gdc_api_url)
    re = json.loads(response.content.decode("utf-8"))

    if "data" not in re or "getPaginatedGenes" not in re["data"] or "genesProper" not in re["data"]["getPaginatedGenes"]:
        return 

    for gene in  json.loads(response.content.decode("utf-8"))["data"]["getPaginatedGenes"]["genesProper"]:
        gene_name = gene["gene_name"]
        print(gene_name)

        gdc_api_url= 'https://pdc.cancer.gov/graphql?query={geneSpectralCount (gene_name: "' + gene_name+ '" acceptDUA: true){gene_id gene_name NCBI_gene_id authority description organism chromosome locus proteins assays spectral_counts { project_submitter_id plex spectral_count distinct_peptide unshared_peptide study_submitter_id pdc_study_id} }}'
        response = requests.get(gdc_api_url)
        re = json.loads(response.content.decode("utf-8"))

        
        if "data" not in re or "geneSpectralCount" not in re["data"]:
            break
        
        geneSpectralCount = re["data"]["geneSpectralCount"]


        for genSpec in geneSpectralCount:
            if "spectral_counts" not in genSpec or "proteins" not in genSpec or "gene_name" not in genSpec and "project_submitter_id" in genSpec["spectral_counts"] :
                break
            # PROTEINE ASSOCIATE AI GENE 
            proteins = (genSpec["proteins"]).split(";")

            ncbi_gene_id = str( genSpec["NCBI_gene_id"])
            gene_name = genSpec["gene_name"] 
            study = genSpec["spectral_counts"]

            studies = []

# ---------------------------------------
            # Ottengo i submitter_id che identificano i vari studi all'interno del database
            # Necessario poichè la query per i geni ottiene soltanto i pdc_study_id
            all_program = dict()
            gdc_api_url = "https://pdc.cancer.gov/graphql?query={allPrograms (acceptDUA: true)  {program_id  program_submitter_id  name projects  {project_id  project_submitter_id  name  studies  {pdc_study_id study_id study_submitter_id submitter_id_name analytical_fraction study_name disease_types primary_sites embargo_date experiment_type acquisition_type} }}}"
            response = requests.get(gdc_api_url)
            prog = json.loads(response.content.decode("utf-8"))

            if "data" not in prog and "allPrograms" not in prog["data"]:
                return 

            # Da qui possiamo prendere i programmi == project e tutti i studi associati ad ogni programma 
            for program in prog["data"]["allPrograms"]:
                studies = []
                if "projects" not in program:
                    break
                for pr in program["projects"]:
                    if "studies" not in pr:
                        break 
                    for st in pr["studies"]:
                        # Qui si puo' applicare il filtro sul primary_site che è relativo ai study 
                        if "study_id" not in st or "study_submitter_id" not in st or "pdc_study_id" not in st :
                            break 
                        all_program[st["pdc_study_id"]] = st["study_submitter_id"]


            # Array degli studi ottenuti dalla query dei geni da convertire                
            for st in study:
                studies.append(st['pdc_study_id'])

            headers = {
                'Accept': 'application/json',
                'Content-Type': 'application/json',
            }
            json_data = {
                'gene_ids': [
                ncbi_gene_id
                ]

            }

            # Effettuo la traduzione da gene_id NCBI in gede_id STANDARD Ensembl ed ottengo il gene_type non presente in PDC 
            gene_tr = json.loads( requests.post('https://api.ncbi.nlm.nih.gov/datasets/v2alpha/gene', headers=headers, json=json_data).content.decode("utf-8") )

            if "reports" in gene_tr and len(gene_tr["reports"]) >=1 and "gene" in gene_tr["reports"][0] and "ensembl_gene_ids" in gene_tr["reports"][0]["gene"] and len(gene_tr["reports"][0]["gene"]["ensembl_gene_ids"]) >= 1 and ( (gene_tr["reports"][0]["gene"]["ensembl_gene_ids"])[0]).startswith('ENSG') and "type" in  gene_tr["reports"][0]["gene"]:
                gene_id = (gene_tr["reports"][0]["gene"]["ensembl_gene_ids"])[0]
                #print(gene_id, gene_name, gene_tr["reports"][0]["gene"]["type"], getGeneType(gene_tr["reports"][0]["gene"]["type"], cursor, conn))
                insertNewGene(gene_id, gene_name, getGeneType(gene_tr["reports"][0]["gene"]["type"], cursor, conn), cursor, conn)
                
                #In gene avremo comunque situazioni del genere:
                #ENSG00000109576.14   AADAT 1  -> Causato dalle transcription che sfrutta GDC 
                #ENSG00000109576    AADAT 1
                

                # Si effettua l'inserimento delle proteine associate a ciascun gene 
                # QUI RICHIAMARE FUNZIONE DI SCRAPING WEB  PASSANDOGLI IL GENE NAME
                for prot in proteins:
                    for st in studies:
                        if st != None:
                            # Vado ad associare ad ogni gene le proteine individuate e in quale studio il gene e le proteine sono state individuate 
                            if checkExistProject(all_program[st],cursor):
                                insertNewGeneProteinStudy(gene_id, prot, all_program[st], cursor, conn)
                                #print(gene_id, prot, all_program[st])

                # FUNZIONA -> DA RIATTIVARE 
                #GetGeneProInformation(gene_name, gene_id, cursor, conn)
                
            # FUNZIONE 
            for st in range(0, len(all_program) ):
                    key = list(all_program.keys())[st]
                    getLog2RatioInfo(key, all_program[key], cursor, conn) 
            

            #else:
                #pass
        
    pass


def sviluppo(cursor, conn):           
    programmi = []
    #programmi = getPrograms()

    #Creo un array studies in modo da evitare l'iterazione dei 3 cicli annidati per le funzioni di ottenimento case e sample
    # I tre cicli annidati avrebbero ciascuno un tempo di esecuzione di circa O(950) -> O(950) * O(950) * O(950) = 857.375.000 iterazioni da eseguire per ogni funzione 
    # In questo modo invece avremo soltanto per la fase di inserimento dei progetti O(950)^3 che è però un tempo trascurabile vista la solo iterazione con il db, 
    #   invece nelle altre funzioni avremo interazioni web e scraping che allungherebbero drasticamente il tempo di esecuzione 
    studies = []
    
    for programma in programmi:
        for progetto in programma.projects:
            for studio in progetto.studies: 
                studies.append(studio)
                # Effettuiamo l'insert degli study che sono l'equivalente dei project all'interno di PDC 
                if not checkExistProject(studio.study_submitter_id, cursor):
                    insertNewProject(studio.study_submitter_id, studio.study_name, cursor, conn)
                #print("finita fase di inserimento progetti")
    x = 0
    #x = len(studies)
    #print(len(studies))
    for st in range( 0, len(studies)):
                x+=1
                print(x , len(studies))
                #print(studio.study_id)
                getCases(studies[st].study_id, studies[st].study_submitter_id, cursor, conn)
                print("----------------finita fase di inserimento case-----------------------")
                getSample(studies[st].study_id, cursor, conn)
                print("----------------finita fase di inserimento sample----------------------")
    
    getGenes(cursor, conn)


# Creo connessione con il database 
cursor, conn = databaseConnection()

sviluppo(cursor, conn)
