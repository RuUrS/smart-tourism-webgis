-- Table: public.luanchuan_boundary
-- DROP TABLE IF EXISTS public.luanchuan_boundary;
CREATE TABLE IF NOT EXISTS public.luanchuan_boundary (
    id integer NOT NULL DEFAULT nextval('luanchuan_boundary_id_seq'::regclass),
    geom geometry(MultiPolygon, 4326),
    adcode integer,
    name character varying COLLATE pg_catalog."default",
    center double precision [],
    centroid double precision [],
    level character varying COLLATE pg_catalog."default",
    acroutes integer [],
    CONSTRAINT luanchuan_boundary_pkey PRIMARY KEY (id)
) TABLESPACE pg_default;
ALTER TABLE IF EXISTS public.luanchuan_boundary OWNER to postgres;
-- Index: sidx_luanchuan_boundary_geom
-- DROP INDEX IF EXISTS public.sidx_luanchuan_boundary_geom;
CREATE INDEX IF NOT EXISTS sidx_luanchuan_boundary_geom ON public.luanchuan_boundary USING gist (geom) TABLESPACE pg_default;