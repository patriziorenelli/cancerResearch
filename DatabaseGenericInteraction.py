'''
Verifica se esiste un id nella tabella biospcimen
'''
def checkExistBiospecimen(id, cursor):
    cursor.execute("SELECT COUNT(*) FROM biospecimen WHERE id = %s", (id,))
    result = cursor.fetchone()
    if result[0] == 0: 
        return False
    return True

'''
Verifica se esiste un progetto all'interno del database
'''
def checkExistProject(id, cursor):
    cursor.execute("SELECT COUNT(*) FROM project WHERE project_id = %s", (id,))
    result = cursor.fetchone()
    if result[0] == 0: 
        return False
    return True

def insertNewProject(id, name, cursor,conn):
    query = "INSERT INTO public.project VALUES ('{}', '{}') ON CONFLICT (project_id) DO NOTHING;".format(id,name)
    cursor.execute(query)

'''
Verifica se esiste un caso all'interno del database
'''
def checkExistCase(id, cursor):
    cursor.execute("SELECT COUNT(*) FROM public.case WHERE case_id = %s", (id,))
    result = cursor.fetchone()
    if result[0] == 0: 
        return False
    return True


'''
Verifica se esiste un file all'interno del database
'''
def checkExistFile(id, cursor):

    cursor.execute("SELECT COUNT(*) FROM analysis WHERE file_id = %s", (id,))
    result = cursor.fetchone()
    if result[0] == 0: 
        return False
    return True


'''
Funzione che si occupa di controllare se un primary site è presente nel db, se non lo trova invoca la funzione che lo aggiunge, ottiene il suo nuovo id e lo restituisce 
'''
def getPrimarySite(data,cursor,conn):
    search_primary_site = "SELECT site_id FROM primary_site WHERE LOWER(site) = LOWER('{}')"
    cursor.execute(search_primary_site.format(data))
    primary_site =  cursor.fetchone()
    if primary_site == None:
            insertNewPrimarySite(data, cursor, conn)
    else:
         return primary_site[0]
    cursor.execute(search_primary_site.format(data)) 
    res = cursor.fetchone()
    return res[0]

'''
Inserisce un nuovo primary site all'interno del db 
'''
def insertNewPrimarySite(data, cursor, conn):
    quer = "INSERT INTO public.primary_site VALUES (DEFAULT, '{}')".format(data)
    cursor.execute(quer)
    conn.commit()

'''
Funzione che si occupa di controllare se un disease è presente nel db, se non lo trova invoca la funzione che lo aggiunge, ottiene il suo nuovo id e lo restituisce 
'''
def getDisease(data, cursor,conn):
    search_disease = "SELECT  disease_id FROM disease WHERE  LOWER(type) = LOWER('{}')"
    cursor.execute(search_disease.format(data))
    diase =  cursor.fetchone()
    if diase == None:
            insertNewDisease(data, cursor, conn)
    else:
         return diase[0]
    cursor.execute(search_disease.format(data)) 
    res = cursor.fetchone()
    return res[0]

'''
Inserisce un nuovo disease all'interno del db 
'''
def insertNewDisease(data, cursor, conn):
    quer = "INSERT INTO public.disease VALUES (DEFAULT, '{}')".format(data)
    cursor.execute(quer)
    conn.commit()


'''
Funzione che si occupa di controllare se una experimental strategy è presente nel db, se non la trova invoca la funzione che lo aggiunge, ottiene il suo nuovo id e lo restituisce 
'''
def getExperimentalStrategy(data, cursor,conn):
    search_exp = "SELECT strategy_id FROM experimental_strategy WHERE  LOWER(strategy) = LOWER('{}')"
    cursor.execute(search_exp.format(data))
    exp =  cursor.fetchone()
    if exp == None:
            insertNewExperimentalStrategy(data, cursor, conn)
    else:
         return exp[0]
    cursor.execute(search_exp.format(data)) 
    res = cursor.fetchone()
    return res[0]

'''
Inserisce una nuova experimental strategy all'interno del db 
'''
def insertNewExperimentalStrategy(data, cursor, conn):
    quer = "INSERT INTO public.experimental_strategy VALUES (DEFAULT, '{}')".format(data)
    cursor.execute(quer)
    conn.commit()


'''
Funzione che si occupa di controllare se una data category è presente nel db, se non lo trova invoca la funzione che la aggiunge, ottiene il suo nuovo id e lo restituisce 
'''
def getDataCategory(data, cursor,conn):
    search_cat = "SELECT category_id FROM data_category WHERE  LOWER(category) = LOWER('{}')"
    cursor.execute(search_cat.format(data))
    cat =  cursor.fetchone()
    if cat == None:
            insertNewDataCategory(data, cursor, conn)
    else:
         return cat[0]
    cursor.execute(search_cat.format(data)) 
    res = cursor.fetchone()
    return res[0]

'''
Inserisce una nuova data category all'interno del db 
'''
def insertNewDataCategory(data, cursor, conn):
    quer = "INSERT INTO public.data_category VALUES (DEFAULT, '{}')".format(data)
    cursor.execute(quer)
    conn.commit()


'''
Funzione che si occupa di controllare se una data type è presente nel db, se non lo trova invoca la funzione che la aggiunge, ottiene il suo nuovo id e lo restituisce 
'''
def getDataType(data, cursor,conn):
    search_data_type = "SELECT type_id FROM data_type WHERE  LOWER(type) = LOWER('{}')"
    cursor.execute(search_data_type.format(data))
    typ =  cursor.fetchone()
    if typ == None:
            insertNewDataType(data, cursor, conn)
    else:
         return typ[0]
    cursor.execute(search_data_type.format(data)) 
    res = cursor.fetchone()
    return res[0]

'''
Inserisce una nuova data type all'interno del db 
'''
def insertNewDataType(data, cursor, conn):
    quer = "INSERT INTO public.data_type VALUES (DEFAULT, '{}')".format(data)
    cursor.execute(quer)
    conn.commit()


'''
Funzione che si occupa di controllare se un gene type è presente nel db, se non lo trova invoca la funzione che la aggiunge, ottiene il suo nuovo id e lo restituisce 
'''
def getGeneType(data, cursor,conn):
    search_exp = "SELECT type_id FROM gene_type WHERE  LOWER(type) = LOWER('{}')"
    cursor.execute(search_exp.format(data))
    gene_type =  cursor.fetchone()
    if gene_type == None:
            insertNewGeneType(data, cursor, conn)
    else:
         return gene_type[0]
    cursor.execute(search_exp.format(data)) 
    res = cursor.fetchone()
    return res[0]

'''
Inserisce un nuovo gene type all'interno del db 
'''
def insertNewGeneType(data, cursor, conn):
    quer = "INSERT INTO public.gene_type VALUES (DEFAULT, '{}')".format(data)
    cursor.execute(quer)
    conn.commit()