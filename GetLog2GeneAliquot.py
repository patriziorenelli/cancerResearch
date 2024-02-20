import requests
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from scipy.stats import zscore
import json
import os 
from DatabaseGenericInteraction import * 


# Funzione per scaricare gli Ensembl Id di tutti i singoli geni, questo è necesario poichè la query utilizzata sotto ritorna solo i nomi dei geni
# Funzione necessaria perchè non è certo che un determinato gene indicato sotto sia già stato salvato all'interno del database e quindi non si può fare una traduzione attraverso il database direttamente 
def getEnsemblId(gene_name):
    # Spostamento nella cartella di Load e apertura del file usato come cache 
    os.chdir("D:\\Users\\Patrizio\\Desktop\\Tirocinio\\Reale\\load")
    with open("Ensembl_Gene_Translation.txt",'a',encoding='utf-8') as f:
        # Costruisco la request
        server = "https://rest.ensembl.org"
        ext = "/xrefs/symbol/homo_sapiens/"+ gene_name +"?"
        r = requests.get(server+ext, headers={ "Content-Type" : "application/json"})
        if not r.ok:
                r.raise_for_status()
        decoded = r.json()
        if len(decoded) == 0:
            return None, None
        f.write(gene_name + ":" + decoded[0]['id']+'\n')
    return gene_name, decoded[0]['id']


def query_pdc(pdc_study_id, data_type):

    # Graphql query passata per l'ottenimento delle informazioni
    query = '''
{ 
    quantDataMatrix(
    pdc_study_id: "''' + pdc_study_id +'''" data_type: "''' + data_type + '''" acceptDUA: true
    )
}'''
    # PDC API url
    url = 'https://pdc.cancer.gov/graphql'

    # Invia una richiesta POST attraverso una graphql query
    pdc_response = requests.post(url, json={'query': query})

    if pdc_response.ok:
        return pdc_response.json()
    else:
        return pdc_response.raise_for_status()

# Per ogni studio possiamo ottenere i log2_ratio e gli unshared_log2_ratio
def getLog2RatioInfo(program_pdc, project_id, cursor, conn):
    data_type = [  'unshared_log2_ratio', 'log2_ratio' ]
    geni_trans = dict()
    for type in data_type:
        decoded = query_pdc(program_pdc, type)

        if 'errors' in decoded:
            continue
        matrix = decoded['data']['quantDataMatrix']
        # pd.DataFrame crea una struttura di 2 dimensioni, avendo così una sorta di tabella da poter navigare nell'estrazione dei dati 
        ga = pd.DataFrame(matrix[1:], columns=matrix[0])
        # lista di liste di gene_name
        gene_name = ga.iloc[:,:1].values

        # per ottenere i gene_name effettivamente bisogna fare così
        #for x in gene_name:
        #    print(x[0])


        # Cerco di utilizzare una sorta di cache per la traduzione gene name : Ensembl gene id perchè non tutti i geni potrebbero essere stati campionati
        try:
            f = ( open("D:\\Users\\Patrizio\\Desktop\\Tirocinio\\Reale\\load\\Ensembl_Gene_Translation.txt", "r") ).read()
            rows = f.split('\n')
            for row in rows:
                r = row.split(':')
                if len(r)>1:
                    geni_trans[r[0]] = r[1]
        except:
            pass
    
        #print(len(geni_trans))

        # Verifico che esiste il file di cache con le traduzioni dei gene_name
        if len(geni_trans) == 0:
            os.chdir("D:\\Users\\Patrizio\\Desktop\\Tirocinio\\Reale\\load")
            with open("Ensembl_Gene_Translation.txt",'w',encoding='utf-8') as f:
                # Effettuo la conversione dei gene name in Ensembl Id che è lo standard usato in tutto il progetto 
                server = "https://rest.ensembl.org"
                for nome in gene_name:
                    ext = "/xrefs/symbol/homo_sapiens/"+nome[0]+"?"
                    r = requests.get(server+ext, headers={ "Content-Type" : "application/json"})
                    if not r.ok:
                        r.raise_for_status()
                    decoded = r.json()
                    geni_trans[nome[0]] = decoded[0]['id']
                    f.write(nome[0] + ":" + decoded[0]['id']+'\n')
                    #print("FILE NUOW")

        

        # Controllo che ho già i corrispondenti Ensembl Id dei geni ottenuti salvati
        # Se ne manca qualcuno lo scarico, salvo nel file usato come cache e lo aggiungo al dizionario usato durante la corrente esecuzione 
        gen_trans_key = list(geni_trans.keys())
        for gen in gene_name:
            if ':' in gen[0]:
                geni_trans[gen[0]] = None
            elif  gen[0] not in gen_trans_key:
                print("Nuovo Gene Trovato " + gen[0])
                gen_name , gene_id = getEnsemblId(gen[0])
                if gen_name != None:
                    geni_trans[gen_name] = gene_id
                
        if not 'Gene/Aliquot' in ga:
            continue

        ga = ga.set_index('Gene/Aliquot')

        # ottengo le colonne 
        oldnames = list(ga.columns)
        newnames = [ x.split(':')[1] for x in oldnames ]

        ga.rename(columns=dict(zip(oldnames, newnames)), inplace=True)
        ga = ga.sort_index(axis=1)

        # con x è possibile prendere i valori di ogni riga e con CPT0000640003 i valori della singola aliquot 
        #print((ga.iloc[0])['CPT0000640003'])
        #print(ga.iloc[0])

        aliquot = list(ga)
        # numero colonne print(len(aliquot))
        # numero righe print(len(ga))

       # print(len(ga), len(aliquot), len(gene_name))

        gen_key = list(geni_trans.keys())
        # BISOGNA RECUPERARE I GENE_ID DEI GENE_NAME
        for x in range(len(ga)):
            for aliq in aliquot:
                #print(aliq)
                # BISOGNA FARE CHECK CHE geni_trans[gene_name[x][0]] esista perchpè alcuni sono None dalla traduzione e quindi non li avrei 
                if gene_name[x][0] not in gen_key or geni_trans[gene_name[x][0]] == None:
                    continue

                #print( geni_trans[gene_name[x][0]] +  " | " + str((ga.iloc[x])[aliq]) +  " | " +  aliq +  " | " +  project_id + " | " +  str(checkExistGene(geni_trans[gene_name[x][0]], cursor) and checkExistProject(project_id, cursor) and str((ga.iloc[x])[aliq]) != "NaN" and checkExistAliquote(aliq, cursor)) )  
                print(checkExistGene(geni_trans[gene_name[x][0]], cursor), checkExistProject(project_id, cursor), str((ga.iloc[x])[aliq]) != "NaN" , checkExistAliquote(aliq, cursor))      
                #if str((ga.iloc[x])[aliq]) == "NaN":
                    #time.sleep(10)
                    #break
                #print(program_pdc, project_id)

                # Effettuiamo un controllo se tutti i valori che dovranno essere usati come primary key sono presenti nel database, in modo da evitare errori nell'esecuzione delle insert o update 
                if checkExistGene(geni_trans[gene_name[x][0]], cursor) and checkExistProject(project_id, cursor) and str((ga.iloc[x])[aliq]) != "NaN" and checkExistAliquote(aliq, cursor):
                    #print( geni_trans[gene_name[x][0]] +  " | " + str((ga.iloc[x])[aliq]) +  " | " +  aliq +  " | " +  project_id)



                    # controllo quale colonna è da aggiornare 
                    if type == 'log2_ratio':
                        if checkExistProtein_PDC(geni_trans[gene_name[x][0]], project_id, aliq,cursor):
                            query = "UPDATE  public.protein_PDC SET log2_ratio = {} WHERE gene_id = '{}' and aliquot = '{}' and project_id = '{}' ;".format(str((ga.iloc[x])[aliq]), geni_trans[gene_name[x][0]], aliq, project_id )
                        else:
                            query = "INSERT INTO public.protein_PDC (gene_id, log2_ratio, aliquot, project_id) VALUES ('{}', {}, '{}', '{}') ON CONFLICT (gene_id,project_id,aliquot) DO NOTHING;".format(geni_trans[gene_name[x][0]], str((ga.iloc[x])[aliq]), aliq, project_id )
                    else: 
                        if checkExistProtein_PDC(geni_trans[gene_name[x][0]], project_id, aliq,cursor):
                            query = "UPDATE  public.protein_PDC SET unshared_log2_ratio = {} WHERE gene_id = '{}' and aliquot = '{}' and project_id = '{}' ;".format(str((ga.iloc[x])[aliq]), geni_trans[gene_name[x][0]], aliq, project_id )
                        else:
                            query = "INSERT INTO public.protein_PDC (gene_id, unshared_log2_ratio, aliquot, project_id) VALUES ('{}', '{}', '{}', '{}') ON CONFLICT (gene_id,project_id,aliquot) DO NOTHING;".format(geni_trans[gene_name[x][0]], str((ga.iloc[x])[aliq]), aliq, project_id )

                    #print(query)
                    cursor.execute(query)
                    conn.commit()
  
        

#getLog2RatioInfo('PDC000127', None, None,None)
                    

