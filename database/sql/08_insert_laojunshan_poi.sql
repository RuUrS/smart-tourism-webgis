CREATE TABLE IF NOT EXISTS public.laojunshan_poi (
    id integer NOT NULL,
    geom geometry(Point, 4326),
    name character varying COLLATE pg_catalog."default",
    type character varying COLLATE pg_catalog."default",
    subtype character varying COLLATE pg_catalog."default",
    lng double precision,
    lat double precision,
    address character varying COLLATE pg_catalog."default",
    description character varying COLLATE pg_catalog."default",
    source character varying COLLATE pg_catalog."default",
    source_url character varying COLLATE pg_catalog."default",
    verify_source character varying COLLATE pg_catalog."default",
    verify_status character varying COLLATE pg_catalog."default",
    remark character varying COLLATE pg_catalog."default",
    CONSTRAINT laojunshan_poi_pkey PRIMARY KEY (id)
) TABLESPACE pg_default;
ALTER TABLE IF EXISTS public.laojunshan_poi OWNER to postgres;
-- Index: sidx_laojunshan_poi_geom
-- DROP INDEX IF EXISTS public.sidx_laojunshan_poi_geom;
CREATE INDEX IF NOT EXISTS sidx_laojunshan_poi_geom ON public.laojunshan_poi USING gist (geom) TABLESPACE pg_default;