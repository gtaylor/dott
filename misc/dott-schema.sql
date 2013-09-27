--
-- PostgreSQL database dump
--

-- Dumped from database version 9.2.4
-- Dumped by pg_dump version 9.2.4
-- Started on 2013-09-27 15:14:50 EDT

SET statement_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;

--
-- TOC entry 172 (class 3079 OID 11734)
-- Name: plpgsql; Type: EXTENSION; Schema: -; Owner: 
--

CREATE EXTENSION IF NOT EXISTS plpgsql WITH SCHEMA pg_catalog;


--
-- TOC entry 1958 (class 0 OID 0)
-- Dependencies: 172
-- Name: EXTENSION plpgsql; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION plpgsql IS 'PL/pgSQL procedural language';


SET search_path = public, pg_catalog;

SET default_tablespace = '';

SET default_with_oids = false;

--
-- TOC entry 168 (class 1259 OID 1105689)
-- Name: dott_accounts; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE dott_accounts (
    username character varying(30) NOT NULL,
    id integer NOT NULL,
    currently_controlling_id integer,
    email character varying(50) NOT NULL,
    password character varying(255) NOT NULL
);


ALTER TABLE public.dott_accounts OWNER TO postgres;

--
-- TOC entry 169 (class 1259 OID 1105692)
-- Name: dott_accounts_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE dott_accounts_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.dott_accounts_id_seq OWNER TO postgres;

--
-- TOC entry 1959 (class 0 OID 0)
-- Dependencies: 169
-- Name: dott_accounts_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE dott_accounts_id_seq OWNED BY dott_accounts.id;


--
-- TOC entry 170 (class 1259 OID 1105694)
-- Name: dott_objects; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
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
    aliases character varying[]
);


ALTER TABLE public.dott_objects OWNER TO postgres;

--
-- TOC entry 171 (class 1259 OID 1105700)
-- Name: dott_objects_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE dott_objects_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.dott_objects_id_seq OWNER TO postgres;

--
-- TOC entry 1960 (class 0 OID 0)
-- Dependencies: 171
-- Name: dott_objects_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE dott_objects_id_seq OWNED BY dott_objects.id;


--
-- TOC entry 1928 (class 2604 OID 1105702)
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY dott_accounts ALTER COLUMN id SET DEFAULT nextval('dott_accounts_id_seq'::regclass);


--
-- TOC entry 1929 (class 2604 OID 1105703)
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY dott_objects ALTER COLUMN id SET DEFAULT nextval('dott_objects_id_seq'::regclass);


--
-- TOC entry 1948 (class 0 OID 1105689)
-- Dependencies: 168
-- Data for Name: dott_accounts; Type: TABLE DATA; Schema: public; Owner: postgres
--



--
-- TOC entry 1961 (class 0 OID 0)
-- Dependencies: 169
-- Name: dott_accounts_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('dott_accounts_id_seq', 1, false);


--
-- TOC entry 1950 (class 0 OID 1105694)
-- Dependencies: 170
-- Data for Name: dott_objects; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO dott_objects VALUES (1, '{}', 'And so it begins...', 'src.game.parents.base_objects.room.RoomObject', NULL, 'room', NULL, NULL, NULL, NULL, NULL, NULL, NULL);


--
-- TOC entry 1962 (class 0 OID 0)
-- Dependencies: 171
-- Name: dott_objects_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('dott_objects_id_seq', 1, true);


--
-- TOC entry 1931 (class 2606 OID 1105705)
-- Name: dott_accounts_id; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY dott_accounts
    ADD CONSTRAINT dott_accounts_id PRIMARY KEY (id);


--
-- TOC entry 1933 (class 2606 OID 1105707)
-- Name: dott_accounts_username; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY dott_accounts
    ADD CONSTRAINT dott_accounts_username UNIQUE (username);


--
-- TOC entry 1936 (class 2606 OID 1105709)
-- Name: dott_objects_id; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY dott_objects
    ADD CONSTRAINT dott_objects_id PRIMARY KEY (id);


--
-- TOC entry 1934 (class 1259 OID 1105710)
-- Name: fki_dott_accounts_currently_controlling_id; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX fki_dott_accounts_currently_controlling_id ON dott_accounts USING btree (currently_controlling_id);


--
-- TOC entry 1937 (class 1259 OID 1105711)
-- Name: fki_dott_objects_controlled_by_account_id_to_id; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX fki_dott_objects_controlled_by_account_id_to_id ON dott_objects USING btree (controlled_by_account_id);


--
-- TOC entry 1938 (class 1259 OID 1105712)
-- Name: fki_dott_objects_destination_id_to_id; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX fki_dott_objects_destination_id_to_id ON dott_objects USING btree (destination_id);


--
-- TOC entry 1939 (class 1259 OID 1105713)
-- Name: fki_dott_objects_location_id_to_id; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX fki_dott_objects_location_id_to_id ON dott_objects USING btree (location_id);


--
-- TOC entry 1940 (class 1259 OID 1105714)
-- Name: fki_dott_objects_original_account_id_to_id; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX fki_dott_objects_original_account_id_to_id ON dott_objects USING btree (originally_controlled_by_account_id);


--
-- TOC entry 1941 (class 1259 OID 1105715)
-- Name: fki_dott_objects_zone_id_to_id; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX fki_dott_objects_zone_id_to_id ON dott_objects USING btree (zone_id);


--
-- TOC entry 1942 (class 2606 OID 1105716)
-- Name: dott_accounts_currently_controlling_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY dott_accounts
    ADD CONSTRAINT dott_accounts_currently_controlling_id FOREIGN KEY (currently_controlling_id) REFERENCES dott_objects(id);


--
-- TOC entry 1943 (class 2606 OID 1105721)
-- Name: dott_objects_controlled_by_account_id_to_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY dott_objects
    ADD CONSTRAINT dott_objects_controlled_by_account_id_to_id FOREIGN KEY (controlled_by_account_id) REFERENCES dott_accounts(id);


--
-- TOC entry 1944 (class 2606 OID 1105726)
-- Name: dott_objects_destination_id_to_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY dott_objects
    ADD CONSTRAINT dott_objects_destination_id_to_id FOREIGN KEY (destination_id) REFERENCES dott_objects(id);


--
-- TOC entry 1945 (class 2606 OID 1105731)
-- Name: dott_objects_location_id_to_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY dott_objects
    ADD CONSTRAINT dott_objects_location_id_to_id FOREIGN KEY (location_id) REFERENCES dott_objects(id);


--
-- TOC entry 1946 (class 2606 OID 1105736)
-- Name: dott_objects_originally_controlled_by_account_id_to_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY dott_objects
    ADD CONSTRAINT dott_objects_originally_controlled_by_account_id_to_id FOREIGN KEY (originally_controlled_by_account_id) REFERENCES dott_accounts(id);


--
-- TOC entry 1947 (class 2606 OID 1105741)
-- Name: dott_objects_zone_id_to_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY dott_objects
    ADD CONSTRAINT dott_objects_zone_id_to_id FOREIGN KEY (zone_id) REFERENCES dott_objects(id);


-- Completed on 2013-09-27 15:14:50 EDT

--
-- PostgreSQL database dump complete
--

