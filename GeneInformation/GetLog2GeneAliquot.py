import requests
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from scipy.stats import zscore



def query_pdc(query):
    # PDC API url
    url = 'https://pdc.cancer.gov/graphql'

    # Send the POST graphql query
    print('Sending query.')
    pdc_response = requests.post(url, json={'query': query})

    # Check the results
    if pdc_response.ok:
        # Decode the response
        return pdc_response.json()
    else:
        # Response not OK, see error
        return pdc_response.raise_for_status()
    

# api dei geni otteniamo i nomi dei geni e poi con questa otteniamo i dati su log2_ratio
    
# BISOGNA ITERARE PER OGNI PROGETTO 
pdc_study_id = 'PDC000127'
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!  FARLO 2 VOLTE METTENDO 'unshared_log2_ratio' !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
data_type = 'log2_ratio' 

quant_data_query = '''
{ 
    quantDataMatrix(
    pdc_study_id: "''' + pdc_study_id +'''" data_type: "''' + data_type + '''" acceptDUA: true
    )
}'''

decoded = query_pdc(quant_data_query)


matrix = decoded['data']['quantDataMatrix']
# print(matrix) -> non si puo' stampare perchè troppo grande 

ga = pd.DataFrame(matrix[1:], columns=matrix[0]).set_index('Gene/Aliquot')

oldnames = list(ga.columns)
newnames = [ x.split(':')[1] for x in oldnames ]

ga.rename(columns=dict(zip(oldnames, newnames)), inplace=True)
ga = ga.sort_index(axis=1)

# con x è possibile prendere i valori di ogni riga e con CPT0000640003 i valori della singola aliquot 
#print((ga.iloc[0])['CPT0000640003'])
    
aliquot = list(ga)
# numero colonne print(len(aliquot))
# numero righe print(len(ga))

for x in range(len(ga)):
    for aliq in aliquot:
        print(aliq + " : "+ str((ga.iloc[x])[aliq]))
