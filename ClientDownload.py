from cdapython import ( Q, columns, unique_terms)
import numpy as np
import pandas as pd


# control + shift (freccia maiusc) + p   -> per cambiare ambiente 

# IL CLIENT ESTRAE SOLO 100 RIGHE ALLA VOLTA BISOGNA ANDARE AD ITERARE PER PRENDERE TUTTI I DATI PRESENTI  

'''
LE QUERY SI DEVONO ITERARE N VOLTE PERCHE' NON PRENDONO TUTTI I VALORI MA SOLO 100 ALLA VOLTA 
                -> per sapere quante volte serve farla si può fare una .count.run prima e poi iterare su quel numero  
                -> res = Q("primary_diagnosis_site = 'Bronchus and lung' FROM subject_identifier_system = 'GDC'").subject.count.run()   e poi prendo res[0]['total']
                
# 1) Per prendere i case relativi ad un site 
# con questo si può andare a popolare la tabella case TRANNE PER IL CAMPO disease 
# In questo caso prendo solo quelli relativi al site Bronchus and lung scritto esattamente così e  [ relativi al sito GDC MI SA DI NO ]

res = Q("primary_diagnosis_site = 'Bronchus and lung' FROM subject_identifier_system = 'GDC'").subject.run()
res = res.to_list()
print(res)

# per prendere  IL CAMPO disease  che manca dall query prima in modo da poter popolare completamente la tabella case  -> ho anche il project_id 
for x in res:
    que = 'researchsubject_id ="' + x['subject_associated_project'][0] + '.'+ x['subject_identifier'][0]['value'] + '"'
    res =Q(que).researchsubject.run()
    #print(res.to_list())
'''

# DALL'ULTIMO LINK GITHUB SI PUA' CERCARE DI FARE UNA CAMPIONATURA 1:1 DEI CAMPI USATI IN GDC GIA'




