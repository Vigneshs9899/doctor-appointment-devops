--
-- PostgreSQL database dump
--

\restrict dNm08r521gRJxCseEbL6dBgOayVnrHjAwZsUOUvabnKHYfBltabLzc6DvpkwlZ3

-- Dumped from database version 15.18 (Debian 15.18-1.pgdg13+1)
-- Dumped by pg_dump version 15.18 (Debian 15.18-1.pgdg13+1)

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

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: appointments; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.appointments (
    id integer NOT NULL,
    name text,
    doctor text,
    appointment_time timestamp without time zone,
    user_id integer,
    status text DEFAULT 'Pending'::text,
    followup_date date,
    symptoms text,
    prescription text,
    doctor_notes text,
    diagnosis text
);


ALTER TABLE public.appointments OWNER TO admin;

--
-- Name: appointments_id_seq; Type: SEQUENCE; Schema: public; Owner: admin
--

CREATE SEQUENCE public.appointments_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.appointments_id_seq OWNER TO admin;

--
-- Name: appointments_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: admin
--

ALTER SEQUENCE public.appointments_id_seq OWNED BY public.appointments.id;


--
-- Name: users; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.users (
    id integer NOT NULL,
    username text,
    password text,
    role text DEFAULT 'patient'::text
);


ALTER TABLE public.users OWNER TO admin;

--
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: admin
--

CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.users_id_seq OWNER TO admin;

--
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: admin
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- Name: appointments id; Type: DEFAULT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.appointments ALTER COLUMN id SET DEFAULT nextval('public.appointments_id_seq'::regclass);


--
-- Name: users id; Type: DEFAULT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- Data for Name: appointments; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.appointments (id, name, doctor, appointment_time, user_id, status, followup_date, symptoms, prescription, doctor_notes, diagnosis) FROM stdin;
2	vignesh	Dr. Shanmuga Loga	2026-04-10 10:00:00	2	Pending	2026-06-30	\N	paracetomol	stay hydrated	tablets & injections
3	vignesh	Dr. Shanmuga Loga	2026-05-18 14:00:00	2	Cancelled	2026-07-10	              fever	dollo	eat healthy foods	tablets & injections
4	vignesh	Dr. Shanmuga Loga	2026-06-20 09:30:00	2	Completed	2026-07-11	              cold	anitbiotic	eat healthy foods	injection
5	vignesh	Dr. Shanmuga Loga	2026-07-05 11:00:00	2	Completed	2026-07-11	cold	para	avoid cold drinks	injection & syrup
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.users (id, username, password, role) FROM stdin;
1	admin@gmail.com	scrypt:32768:8:1$nqWgc7p7k4O2Osnw$f0481bf672ff57b6ba2d61142ba472f07a4308829b845a5320dde1641e4fa170cff8aec1729f84bc85929687ce736d1b80c87b97ad69161399ad1ab2e606e6ca	doctor
2	vignesh@gmail.com	scrypt:32768:8:1$kO85qy0xkp9zdmvI$be9892bb903cea79fdd0926192e8a17043fdf811b8ef0b9b4f42dba404ba4368f256495f30d65130ddb55fdab6f78a6254a11b51381490ba8f5fffb65154d123	patient
\.


--
-- Name: appointments_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.appointments_id_seq', 5, true);


--
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.users_id_seq', 2, true);


--
-- Name: appointments appointments_pkey; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.appointments
    ADD CONSTRAINT appointments_pkey PRIMARY KEY (id);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: users users_username_key; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_username_key UNIQUE (username);


--
-- PostgreSQL database dump complete
--

\unrestrict dNm08r521gRJxCseEbL6dBgOayVnrHjAwZsUOUvabnKHYfBltabLzc6DvpkwlZ3

