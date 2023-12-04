from DatabaseManager import *
import params 
import sys
import requests
import psycopg2
import json
import csv


# PER SCARICARE I FILE SI PUO' USARE L'APPOSITO pdc-client.exe download -m nomeFileManifest 
#       -> MA QUESTO NECESSITA DI UN FILE SPECIFICO PER I SINGOLI FILE, QUESTO FILE MANIFEST PERO' NON SI PUO' SCARICARE 

# ESISTE SOLO IL MODO DI SCARICARE MANUALMENTE IL FILE MANIFEST DA PASSARE POI AL pdc-client? O C'E' ALTRO MODO PER SCARICARE I FILE 


#  I dati su PDC girano intorno ai singoli studi, organizzando i dati in studi basati su su caratteristiche come proteoma o PTM e tipi sperimentali come senza etichetta o TMT 
# In genere gli studi sono specifici per la malattia e per la sede primitiva -> primary site


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

            
gdc_api_url = "https://pdc.cancer.gov/graphql?query={allPrograms (acceptDUA: true)  {program_id  program_submitter_id  name projects  {project_id  project_submitter_id  name  studies  {pdc_study_id study_id study_submitter_id submitter_id_name analytical_fraction study_name disease_types primary_sites embargo_date experiment_type acquisition_type} }}}"
response = requests.get(gdc_api_url)


programs = []

# Da qui possiamo prendere i programmi == project e tutti i studi associati ad ogni programma 
for program in json.loads(response.content.decode("utf-8"))["data"]["allPrograms"]:
    studies = []
    projects = []
    for pr in program["projects"]:
        for st in pr["studies"]:
            # Qui si puo' applicare il filtro sul primary_site che è relativo ai study 
            studies.append(Study(st["study_id"], st["study_submitter_id"], st["study_name"], st["disease_types"],st["primary_sites"] ))
        projects.append(Project(pr["project_id"], pr["project_submitter_id"], pr["name"], studies))
    programs.append( Program(program["program_id"], program["program_submitter_id"],program["name"], projects ) )


# FARE ATTENZIONE AGLI OFFSET E LIMIT DELLE SINGOLE API CHE SONO CAMPI OBBLIGATORI PER QUASI TUTTE 



'''
QUERY DA VEDERE PER ANALYSIS
select file_id, filename, file_size, created_datetime,updated_datetime, project, category, experimental_strategy.strategy_id, type
from analysis join data_category on data_category.category_id = data_category 
			  join  data_type on data_type.type_id = data_type
			  join experimental_strategy on experimental_strategy.strategy_id = experimental_strategy
'''


