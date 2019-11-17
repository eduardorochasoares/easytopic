--
-- PostgreSQL database cluster dump
--

-- Started on 2019-11-17 16:10:05 UTC

SET default_transaction_read_only = off;

SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;

--
-- Roles
--
DO
$do$
BEGIN
   IF NOT EXISTS (
      SELECT                       -- SELECT list can stay empty for this
      FROM   pg_catalog.pg_roles
      WHERE  rolname = 'postgres') THEN

     CREATE ROLE postgres;
     ALTER ROLE postgres WITH SUPERUSER INHERIT CREATEROLE CREATEDB LOGIN REPLICATION BYPASSRLS PASSWORD 'md5354cba921004281fb8d562a63f6fdf70';
   END IF;
END
$do$;







--
-- Databases
--

--
-- Database "template1" dump
--

\connect template1

--
-- PostgreSQL database dump
--

-- Dumped from database version 12.0 (Debian 12.0-2.pgdg100+1)
-- Dumped by pg_dump version 12.0

-- Started on 2019-11-17 16:10:05 UTC

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

-- Completed on 2019-11-17 16:10:05 UTC

--
-- PostgreSQL database dump complete
--

--
-- Database "postgres" dump
--

\connect postgres

--
-- PostgreSQL database dump
--

-- Dumped from database version 12.0 (Debian 12.0-2.pgdg100+1)
-- Dumped by pg_dump version 12.0

-- Started on 2019-11-17 16:10:05 UTC

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
-- TOC entry 203 (class 1259 OID 16386)
-- Name: jobs; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE  public.jobs(
    oid bigint NOT NULL,
    type text NOT NULL,
    status text NOT NULL,
    file_id text,
    project_id integer NOT NULL
);


ALTER TABLE public.jobs OWNER TO postgres;

--
-- TOC entry 202 (class 1259 OID 16384)
-- Name: jobs_oid_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.jobs_oid_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.jobs_oid_seq OWNER TO postgres;

--
-- TOC entry 2923 (class 0 OID 0)
-- Dependencies: 202
-- Name: jobs_oid_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.jobs_oid_seq OWNED BY public.jobs.oid;


--
-- TOC entry 205 (class 1259 OID 16397)
-- Name: project; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE  public.project (
    id bigint NOT NULL,
    video_lesson text NOT NULL
);


ALTER TABLE public.project OWNER TO postgres;

--
-- TOC entry 204 (class 1259 OID 16395)
-- Name: project_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.project_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.project_id_seq OWNER TO postgres;

--
-- TOC entry 2924 (class 0 OID 0)
-- Dependencies: 204
-- Name: project_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.project_id_seq OWNED BY public.project.id;


--
-- TOC entry 2785 (class 2604 OID 16389)
-- Name: jobs oid; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.jobs ALTER COLUMN oid SET DEFAULT nextval('public.jobs_oid_seq'::regclass);


--
-- TOC entry 2786 (class 2604 OID 16400)
-- Name: project id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.project ALTER COLUMN id SET DEFAULT nextval('public.project_id_seq'::regclass);


--
-- TOC entry 2788 (class 2606 OID 16394)
-- Name: jobs jobs_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.jobs
    ADD CONSTRAINT jobs_pkey PRIMARY KEY (oid);


--
-- TOC entry 2790 (class 2606 OID 16402)
-- Name: project project_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.project
    ADD CONSTRAINT project_pkey PRIMARY KEY (id);


--
-- TOC entry 2791 (class 2606 OID 16403)
-- Name: jobs fk_project_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.jobs
    ADD CONSTRAINT fk_project_id FOREIGN KEY (project_id) REFERENCES public.project(id) NOT VALID;


-- Completed on 2019-11-17 16:10:05 UTC

--
-- PostgreSQL database dump complete
--

-- Completed on 2019-11-17 16:10:05 UTC

--
-- PostgreSQL database cluster dump complete
--

