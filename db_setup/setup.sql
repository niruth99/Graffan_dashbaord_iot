
CREATE TABLE device_map (
    id smallint primary key,
    device_name varchar(128),
    manufacturer varchar(128),
    clean_name varchar(128)
);
create unique index mapping_id on device_map(id);
COPY device_map (id, device_name, manufacturer, clean_name) FROM stdin;
1	Apple iPhone 12	Apple	apple_iphone_12
2	Samsung Galaxy M31	Samsung	samsung_galaxy_m31
3	Samsung Galaxy S22	Samsung	samsung_galaxy_s22
4	Googel Pixel 3A	Googel	googel_pixel_3a
5	Samsung Galaxy Tab S8	Samsung	samsung_galaxy_tab_s8
6	Apple iPhone 13 Pro	Apple	apple_iphone_13_pro
7	Apple iPhone 11	Apple	apple_iphone_11
8	Xiaomi Mi A2	Xiaomi	xiaomi_mi_a2
9	Huawei Nova 3I	Huawei	huawei_nova_3i
10	Apple iPad Pro 11 Inch 2018	Apple	apple_ipad_pro_11_inch_2018
11	Apple iPhone 13	Apple	apple_iphone_13
12	Samsung Galaxy J6	Samsung	samsung_galaxy_j6
13	Xiaomi Redmi Note 7	Xiaomi	xiaomi_redmi_note_7
14	Xiaomi Redmi 4	Xiaomi	xiaomi_redmi_4
15	Samsung Galaxy A13	Samsung	samsung_galaxy_a13
16	Samsung Galaxy S6 Edge Plus	Samsung	samsung_galaxy_s6_edge_plus
17	Apple iPhone 7	Apple	apple_iphone_7
18	Apple iPhone X	Apple	apple_iphone_x
19	Apple iPad 8	Apple	apple_ipad_8
20	Google Pixel 7	Google	google_pixel_7_
21	Samsung Galaxy A32	Samsung	samsung_galaxy_a32
22	Apple iPhone 6	Apple	apple_iphone_6
23	Xiaomi Redmi Note 8T	Xiaomi	xiaomi_redmi_note_8t
24	Huawei P20	Huawei	huawei_p20
25	Google Nexus 1   Ph1	Google	google_nexus_1___ph1
26	Samsung Galaxy A33 5G	Samsung	samsung_galaxy_a33_5g
27	Lenovo Thinkpad X13 Gen1	Lenovo	lenovo_thinkpad_x13_gen1
28	Samsung Note 20 Ultra	Samsung	samsung_note_20_ultra
29	Apple Macbook Air M1	Apple	apple_macbook_air_m1
30	Apple iPhone 14 Pro	Apple	apple_iphone_14_pro
31	Huawei Vtr L09	Huawei	huawei_vtr_l09
32	Apple XS	Apple	apple_xs
33	Xiaomi Redmi 5 Plus	Xiaomi	xiaomi_redmi_5_plus
34	Apple Macbook Pro 2015	Apple	apple_macbook_pro_2015
35	Xiaomi Redmi Note 9S	Xiaomi	xiaomi_redmi_note_9s
36	Tplink Smart Globe	Tplink	tplink_smart_globe
37	One Plus Nord	One	one_plus_nord
38	Google Home	Google	google_home
39	iPad 3rd Gen	iPad	ipad_3rd_gen
40	Apple iPhone 14	Apple	apple_iphone_14
41	Samsung Galaxy S4	Samsung	samsung_galaxy_s4
42	Samsung Galaxy S7	Samsung	samsung_galaxy_s7
43	Apple iPad Pro 10 5  2017	Apple	apple_ipad_pro_10_5__2017
44	Tplink Smart Plug	Tplink	tplink_smart_plug
45	Google Nest Mini	Google	google_nest_mini
46	Asus Zenbook 14	Asus	asus_zenbook_14
47	Apple iPhone 12 Pro	Apple	apple_iphone_12_pro
48	Google Pixel 5	Google	google_pixel_5
49	Samsung Galaxy S3	Samsung	samsung_galaxy_s3
50	Huawei Ale L21	Huawei	huawei_ale_l21
51	Xiaomi Poco F1	Xiaomi	xiaomi_poco_f1
52	Apple iPhone XR	Apple	apple_iphone_xr
53	Xiaomi Mi9 Lite	Xiaomi	xiaomi_mi9_lite
54	Samsung Galaxy Tab A8	Samsung	samsung_galaxy_tab_a8
55	Apple iPad Pro 9	Apple	apple_ipad_pro_9
56	Huawei Stf L09	Huawei	huawei_stf_l09
57	Oneplus Nord 5G	Oneplus	oneplus_nord_5g
58	Apple iPhone 6S	Apple	apple_iphone_6s
59	Brilliant Smart Globe	Brilliant	brilliant_smart_globe
60	Samsung Galaxy A73 5G	Samsung	samsung_galaxy_a73_5g
61	Asus Rog Strix G15	Asus	asus_rog_strix_g15
62	Dell Xps 13 9380	Dell	dell_xps_13_9380
63	Msi Gl63 9Rds	Msi	msi_gl63_9rds
64	Apple iPhone 11 Pro	Apple	apple_iphone_11_pro
65	Google Pixel 6 Pro	Google	google_pixel_6_pro
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
he
vendor_specific
vht
interworking
mesh_id
\.


