
CREATE TABLE device_map (
    id smallint primary key,
    device_name varchar(128),
    manufacturer varchar(128),
    clean_name varchar(128)
);
create unique index mapping_id on device_map(id);
COPY device_map (id, device_name, manufacturer, clean_name) FROM stdin;
1	Apple iPad 8	Apple	apple_ipad_8
2	Apple iPhone 11	Apple	apple_iphone_11
3	Apple iPhone 12	Apple	apple_iphone_12
4	Apple iPhone 13 Pro	Apple	apple_iphone_13_pro
5	Apple iPhone 14 Pro	Apple	apple_iphone_14_pro
6	Apple iPhone 6	Apple	apple_iphone_6
7	Apple iPhone 7	Apple	apple_iphone_7
8	Apple iPhone XR	Apple	apple_iphone_xr
9	Apple Macbook Air M1	Apple	apple_macbook_air_m1
10	Apple Macbook Pro 2015	Apple	apple_macbook_pro_2015
11	Apple XS	Apple	apple_xs
12	Asus Zenbook 14	Asus	asus_zenbook_14
13	Dell Xps 13 9380	Dell	dell_xps_13_9380
14	Googel Pixel 3A	Googel	googel_pixel_3a
15	Google Nexus 1   Ph1	Google	google_nexus_1___ph1
16	Google Pixel 5	Google	google_pixel_5
17	Google Pixel 6 Pro	Google	google_pixel_6_pro
18	Google Pixel 7	Google	google_pixel_7_
19	Huawei Ale L21	Huawei	huawei_ale_l21
20	Huawei P20	Huawei	huawei_p20
21	Huawei Stf L09	Huawei	huawei_stf_l09
22	Huawei Vtr L09	Huawei	huawei_vtr_l09
23	iPad 3rd Gen	iPad	ipad_3rd_gen
24	Lenovo Thinkpad X13 Gen1	Lenovo	lenovo_thinkpad_x13_gen1
25	Oneplus Nord 5G	Oneplus	oneplus_nord_5g
26	One Plus Nord	One	one_plus_nord
27	Samsung Galaxy A13	Samsung	samsung_galaxy_a13
28	Samsung Galaxy A32	Samsung	samsung_galaxy_a32
29	Samsung Galaxy A33 5G	Samsung	samsung_galaxy_a33_5g
30	Samsung Galaxy A73 5G	Samsung	samsung_galaxy_a73_5g
31	Samsung Galaxy J6	Samsung	samsung_galaxy_j6
32	Samsung Galaxy M31	Samsung	samsung_galaxy_m31
33	Samsung Galaxy S22	Samsung	samsung_galaxy_s22
34	Samsung Galaxy S3	Samsung	samsung_galaxy_s3
35	Samsung Galaxy S4	Samsung	samsung_galaxy_s4
36	Samsung Galaxy S6 Edge Plus	Samsung	samsung_galaxy_s6_edge_plus
37	Samsung Galaxy S7	Samsung	samsung_galaxy_s7
38	Samsung Galaxy Tab A8	Samsung	samsung_galaxy_tab_a8
39	Samsung Galaxy Tab S8	Samsung	samsung_galaxy_tab_s8
40	Samsung Note 20 Ultra	Samsung	samsung_note_20_ultra
41	Tplink Smart Globe	Tplink	tplink_smart_globe
42	Tplink Smart Plug	Tplink	tplink_smart_plug
43	Xiaomi Mi9 Lite	Xiaomi	xiaomi_mi9_lite
44	Xiaomi Mi A2	Xiaomi	xiaomi_mi_a2
45	Xiaomi Poco F1	Xiaomi	xiaomi_poco_f1
46	Xiaomi Redmi 4	Xiaomi	xiaomi_redmi_4
47	Xiaomi Redmi 5 Plus	Xiaomi	xiaomi_redmi_5_plus
48	Xiaomi Redmi Note 7	Xiaomi	xiaomi_redmi_note_7
49	Xiaomi Redmi Note 8T	Xiaomi	xiaomi_redmi_note_8t
50	Xiaomi Redmi Note 9S	Xiaomi	xiaomi_redmi_note_9s
\.


create TABLE site_map (
    id smallint primary key GENERATED ALWAYS AS IDENTITY,
    name character varying(256),
    lon numeric(12, 9),
    lat numeric(12, 9)
);

CREATE TABLE public.data (
    probe_id bigint primary key GENERATED ALWAYS AS IDENTITY,
    detected_on timestamp without time zone,
    device character varying(256),
    score real[],
    best_device smallint references device_map(id),
    site_id smallint references site_map(id),
    s_db real
);

CREATE TABLE score_breakdown (
    probe_id bigint references public.data(probe_id),
    is_match bool,
    feature character varying(256),
    values real[]
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


