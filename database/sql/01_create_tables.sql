CREATE TABLE IF NOT EXISTS public.tourism_knowledge (
    id integer NOT NULL DEFAULT nextval('tourism_knowledge_id_seq'::regclass),
    title character varying(200) COLLATE pg_catalog."default",
    category character varying(100) COLLATE pg_catalog."default",
    related_poi character varying(100) COLLATE pg_catalog."default",
    content text COLLATE pg_catalog."default",
    source text COLLATE pg_catalog."default",
    source_url text COLLATE pg_catalog."default",
    update_time date,
    content_type character varying(50) COLLATE pg_catalog."default" DEFAULT 'article'::character varying,
    keywords text COLLATE pg_catalog."default",
    verify_status character varying(50) COLLATE pg_catalog."default" DEFAULT '已核验'::character varying,
    created_at timestamp without time zone DEFAULT now(),
    CONSTRAINT tourism_knowledge_pkey PRIMARY KEY (id)
) TABLESPACE pg_default;
ALTER TABLE IF EXISTS public.tourism_knowledge OWNER to postgres;