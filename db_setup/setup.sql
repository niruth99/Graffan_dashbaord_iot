
CREATE TABLE device_map (
    id smallint primary key,
    device_name varchar(128)
);
create unique index mapping_id on device_map(id);
COPY device_map (id, device_name) FROM stdin;
0	apple_ipad_8
1	apple_iphone_11
2	apple_iphone_12
3	apple_iphone_13_pro
4	apple_iphone_14_pro
5	apple_iphone_6
6	apple_iphone_7
7	apple_iphone_xr
8	apple_macbook_air_m1
9	apple_macbook_pro_2015
10	apple_xs
11	asus_zenbook_14
12	dell_xps_13_9380
13	googel_pixel_3a
14	google_nexus_1___ph1
15	google_pixel_5
16	google_pixel_6_pro
17	google_pixel_7_
18	huawei_ale_l21
19	huawei_p20
20	huawei_stf_l09
21	huawei_vtr_l09
22	ipad_3rd_gen
23	lenovo_thinkpad_x13_gen1
24	oneplus_nord_5g
25	one_plus_nord
26	samsung_galaxy_a13
27	samsung_galaxy_a32
28	samsung_galaxy_a33_5g
29	samsung_galaxy_a73_5g
30	samsung_galaxy_j6
31	samsung_galaxy_m31
32	samsung_galaxy_s22
33	samsung_galaxy_s3
34	samsung_galaxy_s4
35	samsung_galaxy_s6_edge_plus
36	samsung_galaxy_s7
37	samsung_galaxy_tab_a8
38	samsung_galaxy_tab_s8
39	samsung_note_20_ultra
40	tplink_smart_globe
41	tplink_smart_plug
42	xiaomi_mi9_lite
43	xiaomi_mi_a2
44	xiaomi_poco_f1
45	xiaomi_redmi_4
46	xiaomi_redmi_5_plus
47	xiaomi_redmi_note_7
48	xiaomi_redmi_note_8t
49	xiaomi_redmi_note_9s
\.


CREATE TABLE public.data (
    probe_id bigint,
    detected_on timestamp without time zone,
    device character varying(256),
    score real[],
    best_device smallint references device_map(id),
    supported_rates_match real[],
    supported_rates_weight real[],
    ext_supported_rates_match real[],
    ext_supported_rates_weight real[],
    ht_match real[],
    ht_weight real[],
    extended_match real[],
    extended_weight real[],
    interworking_match real[],
    interworking_weight real[],
    he_match real[],
    he_weight real[],
    vht_match real[],
    vht_weight real[],
    vendor_specific_match real[],
    vendor_specific_weight real[],
    mesh_id_match real[],
    mesh_id_weight real[]
);

create unique index data_idx on public.data(probe_id);
create index detected_on_idx on public.data(detected_on);


CREATE TABLE available_features (
    feature_name varchar(256)
);
COPY available_features (feature_name) FROM stdin;
supported_rates
ext_supported_rates
ht
extended
interworking
he
vht
vendor_specific
mesh_id
\.


