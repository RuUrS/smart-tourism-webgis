-- View: public.road_network_display
-- DROP VIEW public.road_network_display;
CREATE OR REPLACE VIEW public.road_network_display AS
SELECT id,
    display_name,
    name AS raw_name,
    osm_id,
    code,
    fclass,
    ref,
    oneway,
    maxspeed,
    bridge,
    tunnel,
    road_type,
    walkable,
    source,
    verify_status,
    remark,
    length_m,
    display_level,
    geom
FROM road_network
WHERE geom IS NOT NULL
    AND (
        road_type::text = ANY (
            ARRAY ['main_road'::character varying, 'scenic_road'::character varying, 'trail'::character varying]::text []
        )
    )
    AND length_m >= 20::numeric;
ALTER TABLE public.road_network_display OWNER TO postgres;