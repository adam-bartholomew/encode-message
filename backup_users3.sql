--
-- PostgreSQL database dump
--

-- Dumped from database version 15.4
-- Dumped by pg_dump version 15.3

-- Started on 2023-09-19 12:02:51

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

DROP DATABASE verceldb;
--
-- TOC entry 2555 (class 1262 OID 16386)
-- Name: verceldb; Type: DATABASE; Schema: -; Owner: default
--

CREATE DATABASE verceldb WITH TEMPLATE = template0 ENCODING = 'UTF8' LOCALE_PROVIDER = libc LOCALE = 'C';


ALTER DATABASE verceldb OWNER TO "default";

\connect verceldb

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
-- TOC entry 215 (class 1259 OID 40967)
-- Name: users; Type: TABLE; Schema: public; Owner: default
--

CREATE TABLE public.users (
    id integer NOT NULL,
    username text NOT NULL,
    password text NOT NULL,
    first_name text,
    last_name text,
    email text,
    creation_datetime timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    last_modified_datetime timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    creation_userid text DEFAULT 'system'::text,
    last_modified_userid text DEFAULT 'system'::text,
    sso text
);


ALTER TABLE public.users OWNER TO "default";

--
-- TOC entry 214 (class 1259 OID 40966)
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: default
--

CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.users_id_seq OWNER TO "default";

--
-- TOC entry 2557 (class 0 OID 0)
-- Dependencies: 214
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: default
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- TOC entry 2397 (class 2604 OID 40970)
-- Name: users id; Type: DEFAULT; Schema: public; Owner: default
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- TOC entry 2549 (class 0 OID 40967)
-- Dependencies: 215
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: default
--

INSERT INTO public.users (id, username, password, first_name, last_name, email, creation_datetime, last_modified_datetime, creation_userid, last_modified_userid, sso) VALUES (2, 'test3', '$2b$12$cJw0DACd2brPXiVKC8gfeekflvMTiPqzcNR/9hmRIgEnMdsN92Cg.', 'first name', 'last name2', 'test@email.com', '2023-07-10 19:02:25.181125', '2023-09-06 11:40:05.112449', 'admin', 'test3', NULL);
INSERT INTO public.users (id, username, password, first_name, last_name, email, creation_datetime, last_modified_datetime, creation_userid, last_modified_userid, sso) VALUES (37, 'test45', '$2b$12$NnCMxFWvuxCbAYFa37UXEeNE5K25yL2AcUsNQjCz97dFZRnH7mwNG', NULL, NULL, NULL, '2023-08-23 20:03:37.499932', '2023-08-23 20:03:37.499932', 'system', 'system', NULL);
INSERT INTO public.users (id, username, password, first_name, last_name, email, creation_datetime, last_modified_datetime, creation_userid, last_modified_userid, sso) VALUES (40, 'zsdfdsfg', '$2b$12$SlDk5gCNL.R.AK4oqhUA3emr0ygGTnV/s61W3OH8Df55S2jIiEfGW', NULL, NULL, NULL, '2023-08-23 20:54:16.97071', '2023-08-23 20:54:16.97071', 'system', 'system', NULL);
INSERT INTO public.users (id, username, password, first_name, last_name, email, creation_datetime, last_modified_datetime, creation_userid, last_modified_userid, sso) VALUES (4, 'adamtest', '$2b$12$FikvVgYMghKyukF65v1rJeDlT7V26QGMRpmu7f94hk8HFaaS2arJ6', NULL, NULL, NULL, '2023-07-10 19:34:59.485802', '2023-07-10 19:34:59.485802', 'admin', 'admin', NULL);
INSERT INTO public.users (id, username, password, first_name, last_name, email, creation_datetime, last_modified_datetime, creation_userid, last_modified_userid, sso) VALUES (5, 'testuser1', '$2b$12$hbjsG5CWUFS3ZrB7mn6VJ.bhTT02LUIOji2Hp3fLoIrYGrI0TYA.i', NULL, NULL, NULL, '2023-07-11 18:59:54.812767', '2023-07-11 18:59:54.812767', 'system', 'system', NULL);
INSERT INTO public.users (id, username, password, first_name, last_name, email, creation_datetime, last_modified_datetime, creation_userid, last_modified_userid, sso) VALUES (27, 'new tes6t', '$2b$12$TqA6XEWtiDZQMJ2ZK/4LleEZrvAs96KaJRvV0menwQk.WCBbtah96', NULL, NULL, NULL, '2023-08-06 15:39:18.609995', '2023-08-06 15:39:18.609995', 'system', 'system', NULL);
INSERT INTO public.users (id, username, password, first_name, last_name, email, creation_datetime, last_modified_datetime, creation_userid, last_modified_userid, sso) VALUES (6, 'Genilsonbick', '$2b$12$y33.BBUV0LdMCJG4s.0bnO.oUaQhj6e9HdUv1AgmOAJxdINmJybQO', NULL, NULL, NULL, '2023-07-21 05:49:07.676432', '2023-07-21 05:49:07.676432', 'system', 'system', NULL);
INSERT INTO public.users (id, username, password, first_name, last_name, email, creation_datetime, last_modified_datetime, creation_userid, last_modified_userid, sso) VALUES (7, 'test4', '$2b$12$EAVI/l0sD3VeMi3s/4ZMZu1OXYzggVa4MYEoKLYd0FSkBAFgA3Tv2', NULL, NULL, NULL, '2023-07-24 19:18:51.392693', '2023-07-24 20:10:01.276104', 'system', 'test4', NULL);
INSERT INTO public.users (id, username, password, first_name, last_name, email, creation_datetime, last_modified_datetime, creation_userid, last_modified_userid, sso) VALUES (3, 'test2', '$2b$12$RS03KHLWmWte9qyVPbg1u.oO1e7NyRrP0YuB05TLcI49quZ43awwy', NULL, NULL, NULL, '2023-07-10 19:21:14.124721', '2023-07-24 20:11:43.313828', 'admin', 'test2', NULL);
INSERT INTO public.users (id, username, password, first_name, last_name, email, creation_datetime, last_modified_datetime, creation_userid, last_modified_userid, sso) VALUES (8, 'new_user', '$2b$12$8vDZRvFZOXGhNJ9nm0dY6.U.kHKSFdO4SjY2ZKB65BNLsmIm/YfcC', NULL, NULL, NULL, '2023-08-01 15:03:15.309429', '2023-08-01 15:03:15.309429', 'system', 'system', NULL);
INSERT INTO public.users (id, username, password, first_name, last_name, email, creation_datetime, last_modified_datetime, creation_userid, last_modified_userid, sso) VALUES (36, 'adam.bartholomew17', '$2b$12$cfYVD3fj0h7JANvyZDFwfOQJUUYDAJ/bwX5E4BGqsFqanM8r5FdJy', 'Adam', 'Bartholomew', 'adam.bartholomew17@gmail.com', '2023-08-07 20:05:21.133612', '2023-09-15 15:15:49.69708', 'system', 'adam.bartholomew17', 'Google,Github,Twitch');
INSERT INTO public.users (id, username, password, first_name, last_name, email, creation_datetime, last_modified_datetime, creation_userid, last_modified_userid, sso) VALUES (41, 'test5', '$2b$12$Ar5KYJ8VszyVgh7/Qjdx7.MhGNEyvZVNT3aP8a13fXyVRuEMjq/C.', NULL, NULL, NULL, '2023-09-15 19:26:44.323666', '2023-09-15 19:26:44.323666', 'system', 'system', NULL);


--
-- TOC entry 2558 (class 0 OID 0)
-- Dependencies: 214
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: default
--

SELECT pg_catalog.setval('public.users_id_seq', 41, true);


--
-- TOC entry 2403 (class 2606 OID 40978)
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: default
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- TOC entry 2405 (class 2606 OID 40980)
-- Name: users users_username_key; Type: CONSTRAINT; Schema: public; Owner: default
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_username_key UNIQUE (username);


--
-- TOC entry 2556 (class 0 OID 0)
-- Dependencies: 2555
-- Name: DATABASE verceldb; Type: ACL; Schema: -; Owner: default
--

GRANT ALL ON DATABASE verceldb TO neon_superuser;


-- Completed on 2023-09-19 12:02:54

--
-- PostgreSQL database dump complete
--

