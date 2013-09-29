--
-- PostgreSQL database dump
--

-- Dumped from database version 9.3.0
-- Dumped by pg_dump version 9.3.0
-- Started on 2013-09-29 18:36:27 EDT

SET statement_timeout = 0;
SET lock_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;

--
-- TOC entry 174 (class 3079 OID 11787)
-- Name: plpgsql; Type: EXTENSION; Schema: -; Owner: 
--

CREATE EXTENSION IF NOT EXISTS plpgsql WITH SCHEMA pg_catalog;


--
-- TOC entry 2001 (class 0 OID 0)
-- Dependencies: 174
-- Name: EXTENSION plpgsql; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION plpgsql IS 'PL/pgSQL procedural language';


SET search_path = public, pg_catalog;

SET default_tablespace = '';

SET default_with_oids = false;

--
-- TOC entry 170 (class 1259 OID 16444)
-- Name: dott_accounts; Type: TABLE; Schema: public; Owner: dott; Tablespace: 
--

CREATE TABLE dott_accounts (
    username character varying(30) NOT NULL,
    id integer NOT NULL,
    currently_controlling_id integer,
    email character varying(50) NOT NULL,
    password character varying(255) NOT NULL,
    created_time timestamp with time zone DEFAULT timezone('utc'::text, now()) NOT NULL
);


ALTER TABLE public.dott_accounts OWNER TO dott;

--
-- TOC entry 171 (class 1259 OID 16447)
-- Name: dott_accounts_id_seq; Type: SEQUENCE; Schema: public; Owner: dott
--

CREATE SEQUENCE dott_accounts_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.dott_accounts_id_seq OWNER TO dott;

--
-- TOC entry 2002 (class 0 OID 0)
-- Dependencies: 171
-- Name: dott_accounts_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: dott
--

ALTER SEQUENCE dott_accounts_id_seq OWNED BY dott_accounts.id;


--
-- TOC entry 172 (class 1259 OID 16449)
-- Name: dott_objects; Type: TABLE; Schema: public; Owner: dott; Tablespace: 
--

CREATE TABLE dott_objects (
    id integer NOT NULL,
    attributes json,
    name character varying NOT NULL,
    parent character varying NOT NULL,
    location_id integer,
    base_type character varying(10) NOT NULL,
    originally_controlled_by_account_id integer,
    controlled_by_account_id integer,
    description character varying,
    zone_id integer,
    destination_id integer,
    internal_description character varying,
    aliases character varying[],
    created_time timestamp with time zone DEFAULT timezone('utc'::text, now()) NOT NULL
);


ALTER TABLE public.dott_objects OWNER TO dott;

--
-- TOC entry 173 (class 1259 OID 16455)
-- Name: dott_objects_id_seq; Type: SEQUENCE; Schema: public; Owner: dott
--

CREATE SEQUENCE dott_objects_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.dott_objects_id_seq OWNER TO dott;

--
-- TOC entry 2003 (class 0 OID 0)
-- Dependencies: 173
-- Name: dott_objects_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: dott
--

ALTER SEQUENCE dott_objects_id_seq OWNED BY dott_objects.id;


--
-- TOC entry 1866 (class 2604 OID 16457)
-- Name: id; Type: DEFAULT; Schema: public; Owner: dott
--

ALTER TABLE ONLY dott_accounts ALTER COLUMN id SET DEFAULT nextval('dott_accounts_id_seq'::regclass);


--
-- TOC entry 1868 (class 2604 OID 16458)
-- Name: id; Type: DEFAULT; Schema: public; Owner: dott
--

ALTER TABLE ONLY dott_objects ALTER COLUMN id SET DEFAULT nextval('dott_objects_id_seq'::regclass);


--
-- TOC entry 1871 (class 2606 OID 16460)
-- Name: dott_accounts_id; Type: CONSTRAINT; Schema: public; Owner: dott; Tablespace: 
--

ALTER TABLE ONLY dott_accounts
    ADD CONSTRAINT dott_accounts_id PRIMARY KEY (id);


--
-- TOC entry 1873 (class 2606 OID 16462)
-- Name: dott_accounts_username; Type: CONSTRAINT; Schema: public; Owner: dott; Tablespace: 
--

ALTER TABLE ONLY dott_accounts
    ADD CONSTRAINT dott_accounts_username UNIQUE (username);


--
-- TOC entry 1876 (class 2606 OID 16464)
-- Name: dott_objects_id; Type: CONSTRAINT; Schema: public; Owner: dott; Tablespace: 
--

ALTER TABLE ONLY dott_objects
    ADD CONSTRAINT dott_objects_id PRIMARY KEY (id);


--
-- TOC entry 1874 (class 1259 OID 16465)
-- Name: fki_dott_accounts_currently_controlling_id; Type: INDEX; Schema: public; Owner: dott; Tablespace: 
--

CREATE INDEX fki_dott_accounts_currently_controlling_id ON dott_accounts USING btree (currently_controlling_id);


--
-- TOC entry 1877 (class 1259 OID 16466)
-- Name: fki_dott_objects_controlled_by_account_id_to_id; Type: INDEX; Schema: public; Owner: dott; Tablespace: 
--

CREATE INDEX fki_dott_objects_controlled_by_account_id_to_id ON dott_objects USING btree (controlled_by_account_id);


--
-- TOC entry 1878 (class 1259 OID 16467)
-- Name: fki_dott_objects_destination_id_to_id; Type: INDEX; Schema: public; Owner: dott; Tablespace: 
--

CREATE INDEX fki_dott_objects_destination_id_to_id ON dott_objects USING btree (destination_id);


--
-- TOC entry 1879 (class 1259 OID 16468)
-- Name: fki_dott_objects_location_id_to_id; Type: INDEX; Schema: public; Owner: dott; Tablespace: 
--

CREATE INDEX fki_dott_objects_location_id_to_id ON dott_objects USING btree (location_id);


--
-- TOC entry 1880 (class 1259 OID 16469)
-- Name: fki_dott_objects_original_account_id_to_id; Type: INDEX; Schema: public; Owner: dott; Tablespace: 
--

CREATE INDEX fki_dott_objects_original_account_id_to_id ON dott_objects USING btree (originally_controlled_by_account_id);


--
-- TOC entry 1881 (class 1259 OID 16470)
-- Name: fki_dott_objects_zone_id_to_id; Type: INDEX; Schema: public; Owner: dott; Tablespace: 
--

CREATE INDEX fki_dott_objects_zone_id_to_id ON dott_objects USING btree (zone_id);


--
-- TOC entry 1882 (class 2606 OID 16471)
-- Name: dott_accounts_currently_controlling_id; Type: FK CONSTRAINT; Schema: public; Owner: dott
--

ALTER TABLE ONLY dott_accounts
    ADD CONSTRAINT dott_accounts_currently_controlling_id FOREIGN KEY (currently_controlling_id) REFERENCES dott_objects(id);


--
-- TOC entry 1883 (class 2606 OID 16476)
-- Name: dott_objects_controlled_by_account_id_to_id; Type: FK CONSTRAINT; Schema: public; Owner: dott
--

ALTER TABLE ONLY dott_objects
    ADD CONSTRAINT dott_objects_controlled_by_account_id_to_id FOREIGN KEY (controlled_by_account_id) REFERENCES dott_accounts(id);


--
-- TOC entry 1884 (class 2606 OID 16481)
-- Name: dott_objects_destination_id_to_id; Type: FK CONSTRAINT; Schema: public; Owner: dott
--

ALTER TABLE ONLY dott_objects
    ADD CONSTRAINT dott_objects_destination_id_to_id FOREIGN KEY (destination_id) REFERENCES dott_objects(id);


--
-- TOC entry 1885 (class 2606 OID 16486)
-- Name: dott_objects_location_id_to_id; Type: FK CONSTRAINT; Schema: public; Owner: dott
--

ALTER TABLE ONLY dott_objects
    ADD CONSTRAINT dott_objects_location_id_to_id FOREIGN KEY (location_id) REFERENCES dott_objects(id);


--
-- TOC entry 1886 (class 2606 OID 16491)
-- Name: dott_objects_originally_controlled_by_account_id_to_id; Type: FK CONSTRAINT; Schema: public; Owner: dott
--

ALTER TABLE ONLY dott_objects
    ADD CONSTRAINT dott_objects_originally_controlled_by_account_id_to_id FOREIGN KEY (originally_controlled_by_account_id) REFERENCES dott_accounts(id);


--
-- TOC entry 1887 (class 2606 OID 16496)
-- Name: dott_objects_zone_id_to_id; Type: FK CONSTRAINT; Schema: public; Owner: dott
--

ALTER TABLE ONLY dott_objects
    ADD CONSTRAINT dott_objects_zone_id_to_id FOREIGN KEY (zone_id) REFERENCES dott_objects(id);


-- Completed on 2013-09-29 18:36:32 EDT

--
-- PostgreSQL database dump complete
--

