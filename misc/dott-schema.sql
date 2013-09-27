--
-- PostgreSQL database dump
--

-- Dumped from database version 9.2.4
-- Dumped by pg_dump version 9.2.0
-- Started on 2013-09-27 14:58:28 EDT

SET statement_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;

--
-- TOC entry 172 (class 3079 OID 11995)
-- Name: plpgsql; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS plpgsql WITH SCHEMA pg_catalog;


--
-- TOC entry 2227 (class 0 OID 0)
-- Dependencies: 172
-- Name: EXTENSION plpgsql; Type: COMMENT; Schema: -; Owner: -
--

COMMENT ON EXTENSION plpgsql IS 'PL/pgSQL procedural language';

SET search_path = public, pg_catalog;

SET default_tablespace = '';

SET default_with_oids = false;

--
-- TOC entry 170 (class 1259 OID 16592)
-- Name: dott_accounts; Type: TABLE; Schema: public; Owner: -; Tablespace: 
--

CREATE TABLE dott_accounts (
    username character varying(30) NOT NULL,
    id integer NOT NULL,
    currently_controlling_id integer,
    email character varying(50) NOT NULL,
    password character varying(255) NOT NULL
);


--
-- TOC entry 171 (class 1259 OID 17091)
-- Name: dott_accounts_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE dott_accounts_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 2229 (class 0 OID 0)
-- Dependencies: 171
-- Name: dott_accounts_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE dott_accounts_id_seq OWNED BY dott_accounts.id;


--
-- TOC entry 169 (class 1259 OID 16583)
-- Name: dott_objects; Type: TABLE; Schema: public; Owner: -; Tablespace: 
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


--
-- TOC entry 168 (class 1259 OID 16581)
-- Name: dott_objects_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE dott_objects_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 2230 (class 0 OID 0)
-- Dependencies: 168
-- Name: dott_objects_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE dott_objects_id_seq OWNED BY dott_objects.id;


--
-- TOC entry 2202 (class 2604 OID 17093)
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY dott_accounts ALTER COLUMN id SET DEFAULT nextval('dott_accounts_id_seq'::regclass);


--
-- TOC entry 2201 (class 2604 OID 16586)
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY dott_objects ALTER COLUMN id SET DEFAULT nextval('dott_objects_id_seq'::regclass);


--
-- TOC entry 2211 (class 2606 OID 17102)
-- Name: dott_accounts_id; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace: 
--

ALTER TABLE ONLY dott_accounts
    ADD CONSTRAINT dott_accounts_id PRIMARY KEY (id);


--
-- TOC entry 2213 (class 2606 OID 17104)
-- Name: dott_accounts_username; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace: 
--

ALTER TABLE ONLY dott_accounts
    ADD CONSTRAINT dott_accounts_username UNIQUE (username);


--
-- TOC entry 2204 (class 2606 OID 16591)
-- Name: dott_objects_id; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace: 
--

ALTER TABLE ONLY dott_objects
    ADD CONSTRAINT dott_objects_id PRIMARY KEY (id);


--
-- TOC entry 2214 (class 1259 OID 17110)
-- Name: fki_dott_accounts_currently_controlling_id; Type: INDEX; Schema: public; Owner: -; Tablespace: 
--

CREATE INDEX fki_dott_accounts_currently_controlling_id ON dott_accounts USING btree (currently_controlling_id);


--
-- TOC entry 2205 (class 1259 OID 17156)
-- Name: fki_dott_objects_controlled_by_account_id_to_id; Type: INDEX; Schema: public; Owner: -; Tablespace: 
--

CREATE INDEX fki_dott_objects_controlled_by_account_id_to_id ON dott_objects USING btree (controlled_by_account_id);


--
-- TOC entry 2206 (class 1259 OID 17168)
-- Name: fki_dott_objects_destination_id_to_id; Type: INDEX; Schema: public; Owner: -; Tablespace: 
--

CREATE INDEX fki_dott_objects_destination_id_to_id ON dott_objects USING btree (destination_id);


--
-- TOC entry 2207 (class 1259 OID 17144)
-- Name: fki_dott_objects_location_id_to_id; Type: INDEX; Schema: public; Owner: -; Tablespace: 
--

CREATE INDEX fki_dott_objects_location_id_to_id ON dott_objects USING btree (location_id);


--
-- TOC entry 2208 (class 1259 OID 17150)
-- Name: fki_dott_objects_original_account_id_to_id; Type: INDEX; Schema: public; Owner: -; Tablespace: 
--

CREATE INDEX fki_dott_objects_original_account_id_to_id ON dott_objects USING btree (originally_controlled_by_account_id);


--
-- TOC entry 2209 (class 1259 OID 17162)
-- Name: fki_dott_objects_zone_id_to_id; Type: INDEX; Schema: public; Owner: -; Tablespace: 
--

CREATE INDEX fki_dott_objects_zone_id_to_id ON dott_objects USING btree (zone_id);


--
-- TOC entry 2220 (class 2606 OID 17105)
-- Name: dott_accounts_currently_controlling_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY dott_accounts
    ADD CONSTRAINT dott_accounts_currently_controlling_id FOREIGN KEY (currently_controlling_id) REFERENCES dott_objects(id);


--
-- TOC entry 2217 (class 2606 OID 17151)
-- Name: dott_objects_controlled_by_account_id_to_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY dott_objects
    ADD CONSTRAINT dott_objects_controlled_by_account_id_to_id FOREIGN KEY (controlled_by_account_id) REFERENCES dott_accounts(id);


--
-- TOC entry 2219 (class 2606 OID 17163)
-- Name: dott_objects_destination_id_to_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY dott_objects
    ADD CONSTRAINT dott_objects_destination_id_to_id FOREIGN KEY (destination_id) REFERENCES dott_objects(id);


--
-- TOC entry 2215 (class 2606 OID 17139)
-- Name: dott_objects_location_id_to_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY dott_objects
    ADD CONSTRAINT dott_objects_location_id_to_id FOREIGN KEY (location_id) REFERENCES dott_objects(id);


--
-- TOC entry 2216 (class 2606 OID 17145)
-- Name: dott_objects_originally_controlled_by_account_id_to_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY dott_objects
    ADD CONSTRAINT dott_objects_originally_controlled_by_account_id_to_id FOREIGN KEY (originally_controlled_by_account_id) REFERENCES dott_accounts(id);


--
-- TOC entry 2218 (class 2606 OID 17157)
-- Name: dott_objects_zone_id_to_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY dott_objects
    ADD CONSTRAINT dott_objects_zone_id_to_id FOREIGN KEY (zone_id) REFERENCES dott_objects(id);


-- Completed on 2013-09-27 14:58:28 EDT

--
-- PostgreSQL database dump complete
--

