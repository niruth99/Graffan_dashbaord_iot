CREATE TABLE public.data (
--    invite_code numeric(39,0),
--    created_by bigint,
--    used_by bigint,
    detected_on timestamp without time zone,
--    used_on timestamp without time zone,
    device character varying(256)
);

CREATE TABLE public.timeseries (    
    detected_on timestamp without time zone,
    count int,
    device character varying(256)
);
