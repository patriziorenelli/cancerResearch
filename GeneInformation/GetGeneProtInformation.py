from selenium import webdriver
from time import sleep
import re
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
import random
import pandas as pd

# Con questa funzione otteniamo i valori dei peptide per ogni aliquot associata al gene 
def GetGeneProInformation(geneName):
      # il chromedriver deve essere di versione compatibili con la versione di chrome (applicazione) installata
      p = r"D:\Users\Patrizio\Desktop\Tirocinio\Reale\GeneInformation\chromedriver.exe"
      driver = webdriver.Chrome(p)
      # bisogna mettere il gene_name nel link 
      link = "https://pdc.cancer.gov/pdc/gene/" +geneName
      driver.get(link)
      sleep(5) 
      driver.find_element_by_xpath ("//button[contains( text( ), 'Continue')]").click()
      sleep(3)
      al_current = None
      aliquot_check = True
      cambio = True
      pagina = 0
      while cambio:
            pagina+=1
            # Ottengo codice pagina 
            html_source = driver.page_source
            #driver.quit()
            pos = html_source.index('Biospecimens/Samples in Which the Gene Product Was Detected')
            valid = html_source[pos:]


            tr = BeautifulSoup(valid)
            str_value = tr.get_text(' ')

            valori = (str_value.split('Aliquot')[1]).split("Plex (Dataset alias) Label Study Experiment Type Spectral Counts Distinct Peptides Unshared Peptides Precursor Area Unshared Area Log2 Ratio Unshared Log2 Ratio")
            # Array contenente le Aliquot
            aliquot = [elem for elem in valori[0].split(' ') if elem.strip()]
            str_value = tr.get_text('\n')
            valori = [element.replace('\n', '*') for element in str_value.split('\n')][25:]

            

            # Ottengo i nuovi valori da inserire in una nuova tabella per creare il collegamento gene -> paziente passando per l'aliquot e case 
            aliquot_check = aliquot[0]
            #print(valori)

            # controlliamo il valore di label per capire se mancano dei dati nella tabella di pdc

            lab_c = ["label_free", 
            "itraq_113",
            "itraq_114",
            "itraq_115",
            "itraq_116",
            "itraq_117",
            "itraq_118",
            "itraq_119",
            "itraq_121",
            "tmt_126",
            "tmt_127n",
            "tmt_127c",
            "tmt_128n",
            "tmt_128c",
            "tmt_129n",
            "tmt_129c",
            "tmt_130n",
            "tmt_130c",
            "tmt_131",
            "tmt_131c",
            "tmt_132n",
            "tmt_132c",
            "tmt_133n",
            "tmt_133c",
            "tmt_134n",
            "tmt_134c",
            "tmt_135n",]

            for y in range(0, 10):
                  
                  # fare un for che trova la posizione corretta da usare se y*1 y*2 y*3 y*4 y*5 y*6 y*7 y*8 y*9 y*10 y*11

                  for x in range(0, 12):
                        if valori[0+y*x].lower() in lab_c:
                              break 
                        else:
                              pass
                              
                  const = x   
                              
                  if valori[0+y*const].lower() in lab_c:
                        # tutti i valori da salvare nella tabella 
                        label = valori[0+y*const]
                        study = valori[1+y*const]
                        spectral_count = valori[3+y*const]
                        distinct_peptides = valori[4+y*const]
                        unshared_peptides = valori[5+y*const]
                        print(label +" , "+ study+" , "+ spectral_count+" , "+ distinct_peptides+" , "+ unshared_peptides)
            try:        
                  driver.find_element(By.XPATH,'//*[@id="aliquotRecordTable"]/div/p-paginator/div/a[3]/span').click()
                  sleep(0.86 + random.randint(0,4))
                  #print(pagina)
            except:
                  cambio = False

              

GetGeneProInformation("A1BG")
