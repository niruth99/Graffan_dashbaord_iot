CREATE TABLE public.data (
--    invite_code numeric(39,0),
--    created_by bigint,
--    used_by bigint,
    detected_on timestamp without time zone,
--    used_on timestamp without time zone,
    device character varying(256),
    probe_id bigint
);

create unique index data_idx on public.data(probe_id);
create index detected_on_idx on public.data(detected_on);

CREATE TABLE public.timeseries (    
    detected_on timestamp without time zone,
    count int,
    device character varying(256)
);
