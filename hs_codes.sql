--
-- PostgreSQL database dump
--

\restrict v0qE4TWTde8OgIegMudxxEBgKcHmfs00yHpdEtLLy8AkxQcxzsBDlodgYE5ctzg

-- Dumped from database version 15.16
-- Dumped by pg_dump version 15.16

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Data for Name: hs_codes; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.hs_codes (id, code, description, level, country, mfn_rate, general_rate, vat_rate, consumption_tax, unit, created_at, updated_at, fta_rate, fta_name, fta_countries) FROM stdin;
1	8517	Telephone sets, including smartphones and other apparatus for transmission or reception	tariff	CN	0	0	0.13	\N	\N	2026-02-24 03:40:06.451361+00	\N	\N	\N	\N
2	8517	Telephone sets, including smartphones	tariff	US	0	0	0	\N	\N	2026-02-24 03:40:06.451361+00	\N	\N	\N	\N
3	6203	Men's or boys' suits, ensembles, jackets, blazers, trousers	tariff	CN	0.06	0.06	0.13	\N	\N	2026-02-24 03:40:06.451361+00	\N	\N	\N	\N
4	8471	Automatic data processing machines and units thereof	tariff	CN	0	0	0.13	\N	\N	2026-02-24 03:40:06.451361+00	\N	\N	\N	\N
5	8528	Monitors and projectors, not incorporating television reception apparatus	tariff	CN	0	0	0.13	\N	\N	2026-02-24 03:40:06.451361+00	\N	\N	\N	\N
6	9403	Other furniture and parts thereof	tariff	CN	0	0	0.13	\N	\N	2026-02-24 03:40:06.451361+00	\N	\N	\N	\N
7	6109	T-shirts, singlets and other vests, knitted or crocheted	tariff	CN	0.06	0.06	0.13	\N	\N	2026-02-24 03:40:06.451361+00	\N	\N	\N	\N
8	8704	Motor vehicles for the transport of goods	tariff	CN	0.15	0.15	0.13	\N	\N	2026-02-24 03:40:06.451361+00	\N	\N	\N	\N
9	8708	Parts and accessories of motor vehicles	tariff	CN	0.1	0.1	0.13	\N	\N	2026-02-24 04:15:26.150388+00	\N	\N	\N	\N
10	8502	Electric generating sets and rotary converters	tariff	CN	0.08	0.08	0.13	\N	\N	2026-02-24 04:15:26.150388+00	\N	\N	\N	\N
11	8504	Electrical transformers, static converters, inductors	tariff	CN	0.08	0.08	0.13	\N	\N	2026-02-24 04:15:26.150388+00	\N	\N	\N	\N
12	6204	Women's or girls' suits, ensembles, jackets, blazers	tariff	CN	0.08	0.08	0.13	\N	\N	2026-02-24 04:15:26.150388+00	\N	\N	\N	\N
13	6402	Footwear with outer soles and uppers of rubber or plastics	tariff	CN	0.13	0.13	0.13	\N	\N	2026-02-24 04:15:26.150388+00	\N	\N	\N	\N
14	6403	Footwear with outer soles of rubber, plastics, leather	tariff	CN	0.13	0.13	0.13	\N	\N	2026-02-24 04:15:26.150388+00	\N	\N	\N	\N
15	8471.30	Portable automatic data processing machines, laptops	tariff	CN	0	0	0.13	\N	\N	2026-02-24 04:15:26.150388+00	\N	\N	\N	\N
16	8517.12	Mobile phones including smartphones	tariff	CN	0	0	0.13	\N	\N	2026-02-24 04:15:26.150388+00	\N	\N	\N	\N
17	8517.13	Smartphones with wireless LAN capability	tariff	CN	0	0	0.13	\N	\N	2026-02-24 04:15:26.150388+00	\N	\N	\N	\N
18	8521	Video recording or reproducing apparatus	tariff	CN	0.08	0.08	0.13	\N	\N	2026-02-24 04:15:26.150388+00	\N	\N	\N	\N
19	9504	Video game consoles and machines, arcade games	tariff	CN	0	0	0.13	\N	\N	2026-02-24 04:15:26.150388+00	\N	\N	\N	\N
20	6110	Sweaters, pullovers, cardigans, knitted or crocheted	tariff	CN	0.08	0.08	0.13	\N	\N	2026-02-24 04:15:26.150388+00	\N	\N	\N	\N
21	8703	Motor cars and other motor vehicles, passenger vehicles, 1500-3000cc	tariff	CN	0.15	0.15	0.13	\N	\N	2026-02-24 04:15:55.896619+00	\N	\N	\N	\N
27	8703.21	Passenger cars, spark-ignition engine, 1000-1500cc	tariff	CN	0.15	0.15	0.13	\N	\N	2026-02-24 04:16:15.687394+00	\N	\N	\N	\N
28	8703.22	Passenger cars, spark-ignition engine, 1500-2000cc	tariff	CN	0.15	0.15	0.13	\N	\N	2026-02-24 04:16:15.687394+00	\N	\N	\N	\N
29	8703.23	Passenger cars, spark-ignition engine, 2000-3000cc	tariff	CN	0.15	0.15	0.13	\N	\N	2026-02-24 04:16:15.687394+00	\N	\N	\N	\N
30	8703.24	Passenger cars, spark-ignition engine, over 3000cc	tariff	CN	0.25	0.25	0.13	\N	\N	2026-02-24 04:16:15.687394+00	\N	\N	\N	\N
33	8703	Motor cars and other motor vehicles, passenger vehicles	tariff	EU	0.1	0.1	0.2	\N	\N	2026-02-24 23:29:57.916405+00	\N	\N	\N	\N
34	8703.21	Passenger cars, spark-ignition engine, 1000-1500cc	tariff	EU	0.1	0.1	0.2	\N	\N	2026-02-24 23:29:57.916405+00	\N	\N	\N	\N
35	8703.22	Passenger cars, spark-ignition engine, 1500-2000cc	tariff	EU	0.1	0.1	0.2	\N	\N	2026-02-24 23:29:57.916405+00	\N	\N	\N	\N
36	8703.23	Passenger cars, spark-ignition engine, 2000-3000cc	tariff	EU	0.1	0.1	0.2	\N	\N	2026-02-24 23:29:57.916405+00	\N	\N	\N	\N
37	8703.24	Passenger cars, spark-ignition engine, over 3000cc	tariff	EU	0.1	0.1	0.2	\N	\N	2026-02-24 23:29:57.916405+00	\N	\N	\N	\N
38	8703.31	Passenger cars, diesel engine, 1500-2500cc	tariff	EU	0.1	0.1	0.2	\N	\N	2026-02-24 23:29:57.916405+00	\N	\N	\N	\N
39	8703.32	Passenger cars, diesel engine, 2500cc and above	tariff	EU	0.1	0.1	0.2	\N	\N	2026-02-24 23:29:57.916405+00	\N	\N	\N	\N
40	8703.90	Other passenger vehicles including electric vehicles	tariff	EU	0.1	0.1	0.2	\N	\N	2026-02-24 23:29:57.916405+00	\N	\N	\N	\N
41	8517	Telephone sets, including smartphones and other apparatus	tariff	EU	0	0	0.2	\N	\N	2026-02-24 23:29:57.916405+00	\N	\N	\N	\N
42	8517.12	Mobile phones including smartphones	tariff	EU	0	0	0.2	\N	\N	2026-02-24 23:29:57.916405+00	\N	\N	\N	\N
43	8517.13	Smartphones with wireless LAN capability	tariff	EU	0	0	0.2	\N	\N	2026-02-24 23:29:57.916405+00	\N	\N	\N	\N
44	8471	Automatic data processing machines and units thereof	tariff	EU	0	0	0.2	\N	\N	2026-02-24 23:29:57.916405+00	\N	\N	\N	\N
45	8471.30	Portable automatic data processing machines, laptops, tablets	tariff	EU	0	0	0.2	\N	\N	2026-02-24 23:29:57.916405+00	\N	\N	\N	\N
46	8528	Monitors and projectors, not incorporating television reception	tariff	EU	0.14	0.14	0.2	\N	\N	2026-02-24 23:29:57.916405+00	\N	\N	\N	\N
47	8521	Video recording or reproducing apparatus	tariff	EU	0.135	0.135	0.2	\N	\N	2026-02-24 23:29:57.916405+00	\N	\N	\N	\N
48	8704	Motor vehicles for the transport of goods	tariff	EU	0.22	0.22	0.2	\N	\N	2026-02-24 23:29:57.916405+00	\N	\N	\N	\N
49	8708	Parts and accessories of motor vehicles	tariff	EU	0.045	0.045	0.2	\N	\N	2026-02-24 23:29:57.916405+00	\N	\N	\N	\N
50	6203	Mens or boys suits, ensembles, jackets, blazers, trousers	tariff	EU	0.12	0.12	0.2	\N	\N	2026-02-24 23:29:57.916405+00	\N	\N	\N	\N
51	6204	Womens or girls suits, ensembles, jackets, blazers	tariff	EU	0.12	0.12	0.2	\N	\N	2026-02-24 23:29:57.916405+00	\N	\N	\N	\N
52	6109	T-shirts, singlets and other vests, knitted or crocheted	tariff	EU	0.12	0.12	0.2	\N	\N	2026-02-24 23:29:57.916405+00	\N	\N	\N	\N
53	6110	Sweaters, pullovers, cardigans, knitted or crocheted	tariff	EU	0.12	0.12	0.2	\N	\N	2026-02-24 23:29:57.916405+00	\N	\N	\N	\N
54	6402	Footwear with outer soles and uppers of rubber or plastics	tariff	EU	0.17	0.17	0.2	\N	\N	2026-02-24 23:29:57.916405+00	\N	\N	\N	\N
55	6403	Footwear with outer soles of rubber, plastics, leather	tariff	EU	0.08	0.08	0.2	\N	\N	2026-02-24 23:29:57.916405+00	\N	\N	\N	\N
56	9403	Other furniture and parts thereof	tariff	EU	0	0	0.2	\N	\N	2026-02-24 23:29:57.916405+00	\N	\N	\N	\N
57	9504	Video game consoles and machines, arcade games, gaming	tariff	EU	0	0	0.2	\N	\N	2026-02-24 23:29:57.916405+00	\N	\N	\N	\N
58	8502	Electric generating sets and rotary converters	tariff	EU	0.027	0.027	0.2	\N	\N	2026-02-24 23:29:57.916405+00	\N	\N	\N	\N
59	8504	Electrical transformers, static converters, inductors	tariff	EU	0.027	0.027	0.2	\N	\N	2026-02-24 23:29:57.916405+00	\N	\N	\N	\N
\.


--
-- Name: hs_codes_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.hs_codes_id_seq', 59, true);


--
-- PostgreSQL database dump complete
--

\unrestrict v0qE4TWTde8OgIegMudxxEBgKcHmfs00yHpdEtLLy8AkxQcxzsBDlodgYE5ctzg

