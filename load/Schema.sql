CREATE TABLE IF NOT EXISTS public.aliquote
(
    aliquote_id text COLLATE pg_catalog."default" NOT NULL,
    analyte_id text COLLATE pg_catalog."default" NOT NULL,
    concentration numeric,
    CONSTRAINT aliquote_pkey PRIMARY KEY (aliquote_id)
);

CREATE TABLE IF NOT EXISTS public.analysis
(
    file_id text COLLATE pg_catalog."default" NOT NULL,
    filename text COLLATE pg_catalog."default",
    file_size numeric,
    created_datetime date,
    updated_datetime date,
    project text COLLATE pg_catalog."default" NOT NULL,
    data_category integer,
    data_type integer,
    experimental_strategy integer,
    CONSTRAINT "File_pkey" PRIMARY KEY (file_id)
);

CREATE TABLE IF NOT EXISTS public.analysis_entity
(
    analysis text COLLATE pg_catalog."default" NOT NULL,
    biospecimen_id text COLLATE pg_catalog."default" NOT NULL,
    CONSTRAINT analysis_entity_pkey PRIMARY KEY (analysis, biospecimen_id)
);

CREATE TABLE IF NOT EXISTS public.analyte
(
    analyte_id text COLLATE pg_catalog."default" NOT NULL,
    portion_id text COLLATE pg_catalog."default" NOT NULL,
    concentration numeric,
    CONSTRAINT analyte_pkey PRIMARY KEY (analyte_id)
);

CREATE TABLE IF NOT EXISTS public.biospecimen
(
    id text COLLATE pg_catalog."default" NOT NULL,
    "case" text COLLATE pg_catalog."default" NOT NULL,
    type integer NOT NULL,
    CONSTRAINT biospecimen_pkey PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS public.biospecimen_type
(
    type_id integer NOT NULL GENERATED ALWAYS AS IDENTITY ( INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 2147483647 CACHE 1 ),
    type text COLLATE pg_catalog."default",
    CONSTRAINT "Biospecimen_Type_pkey" PRIMARY KEY (type_id)

);

CREATE TABLE IF NOT EXISTS public."case"
(
    case_id text COLLATE pg_catalog."default" NOT NULL,
    ethnicity text COLLATE pg_catalog."default",
    gender text COLLATE pg_catalog."default",
    race text COLLATE pg_catalog."default",
    vital_status text COLLATE pg_catalog."default",
    project text COLLATE pg_catalog."default" NOT NULL,
    site integer,
    disease integer,
    CONSTRAINT "Case_pkey" PRIMARY KEY (case_id)
);

CREATE TABLE IF NOT EXISTS public.data_category
(
    category_id integer NOT NULL GENERATED ALWAYS AS IDENTITY ( INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 2147483647 CACHE 1 ),
    category text COLLATE pg_catalog."default",
    CONSTRAINT "Data_Category_pkey" PRIMARY KEY (category_id)
);

CREATE TABLE IF NOT EXISTS public.data_type
(
    type_id integer NOT NULL GENERATED ALWAYS AS IDENTITY ( INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 2147483647 CACHE 1 ),
    type text COLLATE pg_catalog."default",
    CONSTRAINT "Data_Type_pkey" PRIMARY KEY (type_id)
);

CREATE TABLE IF NOT EXISTS public.disease
(
    disease_id integer NOT NULL GENERATED ALWAYS AS IDENTITY ( INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 2147483647 CACHE 1 ),
    type text COLLATE pg_catalog."default",
    CONSTRAINT "Disease_pkey" PRIMARY KEY (disease_id)
);

CREATE TABLE IF NOT EXISTS public.experimental_strategy
(
    strategy_id integer NOT NULL GENERATED ALWAYS AS IDENTITY ( INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 2147483647 CACHE 1 ),
    strategy text COLLATE pg_catalog."default",
    CONSTRAINT "Experimental_Strategy_pkey" PRIMARY KEY (strategy_id)
);

CREATE TABLE IF NOT EXISTS public.gene
(
    gene_id text COLLATE pg_catalog."default" NOT NULL,
    name text COLLATE pg_catalog."default",
    type integer,
    CONSTRAINT "Gene_pkey" PRIMARY KEY (gene_id)
);

CREATE TABLE IF NOT EXISTS public.gene_expression_file
(
    analysis text COLLATE pg_catalog."default" NOT NULL,
    gene text COLLATE pg_catalog."default" NOT NULL,
    tpm numeric,
    fpkm numeric,
    fpkm_uq numeric,
    unstranded integer,
    stranded_first integer,
    stranded_second integer,
    CONSTRAINT keys PRIMARY KEY (analysis, gene)
);

CREATE TABLE IF NOT EXISTS public.gene_type
(
    type_id integer NOT NULL GENERATED ALWAYS AS IDENTITY ( INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 2147483647 CACHE 1 ),
    type text COLLATE pg_catalog."default",
    CONSTRAINT "Gene_Type_pkey" PRIMARY KEY (type_id)
);

CREATE TABLE IF NOT EXISTS public.portion
(
    portion_id text COLLATE pg_catalog."default" NOT NULL,
    sample_id text COLLATE pg_catalog."default" NOT NULL,
    CONSTRAINT portion_pkey PRIMARY KEY (portion_id)
);

CREATE TABLE IF NOT EXISTS public.primary_site
(
    site_id integer NOT NULL GENERATED ALWAYS AS IDENTITY ( INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 2147483647 CACHE 1 ),
    site text COLLATE pg_catalog."default",
    CONSTRAINT "Primary_Site_pkey" PRIMARY KEY (site_id)
);

CREATE TABLE IF NOT EXISTS public.project
(
    project_id text COLLATE pg_catalog."default" NOT NULL,
    name text COLLATE pg_catalog."default",
    CONSTRAINT "Project_pkey" PRIMARY KEY (project_id)
);

CREATE TABLE IF NOT EXISTS public.protein
(
    agid text COLLATE pg_catalog."default" NOT NULL,
    lab_id integer,
    catalog_number text COLLATE pg_catalog."default",
    set_id text COLLATE pg_catalog."default",
    peptide_target text COLLATE pg_catalog."default",
    CONSTRAINT "Protein_pkey" PRIMARY KEY (agid)
);

CREATE TABLE IF NOT EXISTS public.protein_expression_file
(
    analysis text COLLATE pg_catalog."default" NOT NULL,
    protein text COLLATE pg_catalog."default" NOT NULL,
    expression numeric,
    CONSTRAINT "Protein_Expression_File_pkey" PRIMARY KEY (analysis, protein)
);

CREATE TABLE IF NOT EXISTS public.sample
(
    sample_id text COLLATE pg_catalog."default" NOT NULL,
    type integer,
    tumor integer,
    CONSTRAINT sample_pkey PRIMARY KEY (sample_id)
);

CREATE TABLE IF NOT EXISTS public.sample_type
(
    type_id integer NOT NULL,
    type text COLLATE pg_catalog."default",
    CONSTRAINT "Sample_Type_pkey" PRIMARY KEY (type_id)
);

CREATE TABLE IF NOT EXISTS public.tumor
(
    tumor_code_id integer NOT NULL,
    code text COLLATE pg_catalog."default",
    descriptor text COLLATE pg_catalog."default",
    CONSTRAINT "Tumor_pkey" PRIMARY KEY (tumor_code_id)
);

ALTER TABLE IF EXISTS public.aliquote
    ADD CONSTRAINT aliquote_aliquote_id_fkey FOREIGN KEY (aliquote_id)
    REFERENCES public.biospecimen (id) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION
    NOT VALID;


ALTER TABLE IF EXISTS public.aliquote
    ADD CONSTRAINT aliquote_analyte_id_fkey FOREIGN KEY (analyte_id)
    REFERENCES public.analyte (analyte_id) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION
    NOT VALID;


ALTER TABLE IF EXISTS public.analysis
    ADD CONSTRAINT "Data_Category" FOREIGN KEY (data_category)
    REFERENCES public.data_category (category_id) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION
    NOT VALID;


ALTER TABLE IF EXISTS public.analysis
    ADD CONSTRAINT "Data_Type" FOREIGN KEY (data_type)
    REFERENCES public.data_type (type_id) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION
    NOT VALID;


ALTER TABLE IF EXISTS public.analysis
    ADD CONSTRAINT "Experimental_Strategy" FOREIGN KEY (experimental_strategy)
    REFERENCES public.experimental_strategy (strategy_id) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION
    NOT VALID;


ALTER TABLE IF EXISTS public.analysis
    ADD CONSTRAINT "Project" FOREIGN KEY (project)
    REFERENCES public.project (project_id) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION;


ALTER TABLE IF EXISTS public.analysis_entity
    ADD CONSTRAINT "File" FOREIGN KEY (analysis)
    REFERENCES public.analysis (file_id) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION;


ALTER TABLE IF EXISTS public.analysis_entity
    ADD CONSTRAINT analysis_entity_biospecimen_id_fkey FOREIGN KEY (biospecimen_id)
    REFERENCES public.biospecimen (id) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION
    NOT VALID;


ALTER TABLE IF EXISTS public.analyte
    ADD CONSTRAINT analyte_analyte_id_fkey FOREIGN KEY (analyte_id)
    REFERENCES public.biospecimen (id) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION
    NOT VALID;



ALTER TABLE IF EXISTS public.analyte
    ADD CONSTRAINT "analyte_portion_Id_fkey" FOREIGN KEY (portion_id)
    REFERENCES public.portion (portion_id) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION
    NOT VALID;


ALTER TABLE IF EXISTS public.biospecimen
    ADD CONSTRAINT "Case" FOREIGN KEY ("case")
    REFERENCES public."case" (case_id) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION
    NOT VALID;


ALTER TABLE IF EXISTS public.biospecimen
    ADD CONSTRAINT "Type" FOREIGN KEY (type)
    REFERENCES public.biospecimen_type (type_id) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION
    NOT VALID;


ALTER TABLE IF EXISTS public."case"
    ADD CONSTRAINT "case_Disease_fkey" FOREIGN KEY (disease)
    REFERENCES public.disease (disease_id) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION
    NOT VALID;


ALTER TABLE IF EXISTS public."case"
    ADD CONSTRAINT "case_Site_fkey" FOREIGN KEY (site)
    REFERENCES public.primary_site (site_id) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION
    NOT VALID;


ALTER TABLE IF EXISTS public.gene
    ADD CONSTRAINT "Type" FOREIGN KEY (type)
    REFERENCES public.gene_type (type_id) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION
    NOT VALID;


ALTER TABLE IF EXISTS public.gene_expression_file
    ADD CONSTRAINT "File" FOREIGN KEY (analysis)
    REFERENCES public.analysis (file_id) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION;


ALTER TABLE IF EXISTS public.gene_expression_file
    ADD CONSTRAINT "Gene" FOREIGN KEY (gene)
    REFERENCES public.gene (gene_id) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION;


ALTER TABLE IF EXISTS public.portion
    ADD CONSTRAINT portion_portion_id_fkey FOREIGN KEY (portion_id)
    REFERENCES public.biospecimen (id) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION
    NOT VALID;



ALTER TABLE IF EXISTS public.portion
    ADD CONSTRAINT portion_sample_id_fkey FOREIGN KEY (sample_id)
    REFERENCES public.sample (sample_id) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION
    NOT VALID;


ALTER TABLE IF EXISTS public.protein_expression_file
    ADD CONSTRAINT "File" FOREIGN KEY (analysis)
    REFERENCES public.analysis (file_id) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION;


ALTER TABLE IF EXISTS public.protein_expression_file
    ADD CONSTRAINT "Protein" FOREIGN KEY (protein)
    REFERENCES public.protein (agid) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION;


ALTER TABLE IF EXISTS public.sample
    ADD CONSTRAINT "Tumor" FOREIGN KEY (tumor)
    REFERENCES public.tumor (tumor_code_id) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION;


ALTER TABLE IF EXISTS public.sample
    ADD CONSTRAINT "Type" FOREIGN KEY (type)
    REFERENCES public.sample_type (type_id) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION;


ALTER TABLE IF EXISTS public.sample
    ADD CONSTRAINT sample_sample_id_fkey FOREIGN KEY (sample_id)
    REFERENCES public.biospecimen (id) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION
    NOT VALID;

