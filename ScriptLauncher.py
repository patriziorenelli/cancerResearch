
# SI POTREBBE USARE PER LANCIARE GLI SCRIPT E CONTROLLARE LO STATO DEGLI SCRIPT PER RILANCIARLI IN CASO DI ERRORI O CESSAZIONE DELLE CONNESSIONI 
# Da questo file lanciare IN UNA NUOVA CONSOLE il file di GDC_DownloadData.py e capire quando va in errore o cose del genere 
# pid: 17448 -> indica solo python3.9
# Bisogna capire lo stato della funzione che viene eseguita
# -> Al posto di fare i continue o break si potrebbero fare dei return -> per errore di connessione "quando si fanno le get" ritornare "Error server connection" e ritentare 
#                                                                       -> per gli altri errori restituire errore sul fetch dei dati o simile


from GDC_DownloadData import *
from PDC_DownloadData import *




#while True:
    #download_and_process_expression_data(params)

