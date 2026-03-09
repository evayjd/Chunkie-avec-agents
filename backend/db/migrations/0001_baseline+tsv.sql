--
-- PostgreSQL database dump
--

\restrict xEdO0Mua8a6XXdTEWff5xtgtnzrIafSxJOFFlzlVwQUFuCrqiU9LMl5mHjbrFvc

-- Dumped from database version 16.12 (Homebrew)
-- Dumped by pg_dump version 16.12 (Homebrew)

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
-- Name: vector; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS vector WITH SCHEMA public;


--
-- Name: EXTENSION vector; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION vector IS 'vector data type and ivfflat and hnsw access methods';


--
-- Name: chunks_tsv_trigger(); Type: FUNCTION; Schema: public; Owner: dyj
--

CREATE FUNCTION public.chunks_tsv_trigger() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
  NEW.tsv := to_tsvector('simple', NEW.content);
  RETURN NEW;
END
$$;


ALTER FUNCTION public.chunks_tsv_trigger() OWNER TO dyj;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: chunks; Type: TABLE; Schema: public; Owner: dyj
--

CREATE TABLE public.chunks (
    id uuid NOT NULL,
    document_id uuid NOT NULL,
    chunk_index integer NOT NULL,
    content text NOT NULL,
    page_start integer,
    page_end integer,
    section character varying(255),
    metadata_json jsonb,
    embedding public.vector(384),
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    tsv tsvector
);


ALTER TABLE public.chunks OWNER TO dyj;

--
-- Name: documents; Type: TABLE; Schema: public; Owner: dyj
--

CREATE TABLE public.documents (
    id uuid NOT NULL,
    filename character varying(255) NOT NULL,
    file_type character varying(50) NOT NULL,
    file_path character varying(1000) NOT NULL,
    raw_text text,
    cleaned_text text,
    metadata_json jsonb,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.documents OWNER TO dyj;

--
-- Name: chunks chunks_pkey; Type: CONSTRAINT; Schema: public; Owner: dyj
--

ALTER TABLE ONLY public.chunks
    ADD CONSTRAINT chunks_pkey PRIMARY KEY (id);


--
-- Name: documents documents_pkey; Type: CONSTRAINT; Schema: public; Owner: dyj
--

ALTER TABLE ONLY public.documents
    ADD CONSTRAINT documents_pkey PRIMARY KEY (id);


--
-- Name: idx_chunks_tsv; Type: INDEX; Schema: public; Owner: dyj
--

CREATE INDEX idx_chunks_tsv ON public.chunks USING gin (tsv);


--
-- Name: ix_chunks_document_id; Type: INDEX; Schema: public; Owner: dyj
--

CREATE INDEX ix_chunks_document_id ON public.chunks USING btree (document_id);


--
-- Name: chunks tsv_update; Type: TRIGGER; Schema: public; Owner: dyj
--

CREATE TRIGGER tsv_update BEFORE INSERT OR UPDATE ON public.chunks FOR EACH ROW EXECUTE FUNCTION public.chunks_tsv_trigger();


--
-- Name: chunks chunks_document_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: dyj
--

ALTER TABLE ONLY public.chunks
    ADD CONSTRAINT chunks_document_id_fkey FOREIGN KEY (document_id) REFERENCES public.documents(id) ON DELETE CASCADE;


--
-- PostgreSQL database dump complete
--

\unrestrict xEdO0Mua8a6XXdTEWff5xtgtnzrIafSxJOFFlzlVwQUFuCrqiU9LMl5mHjbrFvc

