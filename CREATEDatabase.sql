--
-- PostgreSQL database dump
--

-- Dumped from database version 13.15 (Raspbian 13.15-0+deb11u1)
-- Dumped by pg_dump version 16.0

-- Started on 2024-10-23 22:34:29

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
-- TOC entry 4 (class 2615 OID 2200)
-- Name: public; Type: SCHEMA; Schema: -; Owner: postgres
--

-- *not* creating schema, since initdb creates it


ALTER SCHEMA public OWNER TO postgres;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- TOC entry 200 (class 1259 OID 17273)
-- Name: Должность; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public."Должность" (
    "Код_должности" integer NOT NULL,
    "Наименование_должности" character varying(20)
);


ALTER TABLE public."Должность" OWNER TO postgres;

--
-- TOC entry 201 (class 1259 OID 17278)
-- Name: Заказ; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public."Заказ" (
    "Код_заказа" integer NOT NULL,
    "Статус_заказа" character varying(20),
    "Код_сотрудника" integer,
    "Код_клиента" integer,
    "Сумма" integer,
    "Дата_доставки" date
);


ALTER TABLE public."Заказ" OWNER TO postgres;

--
-- TOC entry 202 (class 1259 OID 17283)
-- Name: Клиент; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public."Клиент" (
    "Код_клиента" integer NOT NULL,
    "Название" character varying(20),
    "Адрес" character varying(20),
    "Контактное_лицо" character varying(20),
    e_mail character varying(20),
    "Договор" character varying(20),
    "Примечание" character varying(20),
    "ИНН" integer,
    "Телефон" integer
);


ALTER TABLE public."Клиент" OWNER TO postgres;

--
-- TOC entry 203 (class 1259 OID 17288)
-- Name: Сотрудники; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public."Сотрудники" (
    "Код_сотрудника" integer NOT NULL,
    "ФИО" character varying(20),
    "Адрес" character varying(20),
    "Паспорт" character varying(20),
    "Телефон" integer,
    "Код_должности" integer
);


ALTER TABLE public."Сотрудники" OWNER TO postgres;

--
-- TOC entry 204 (class 1259 OID 17293)
-- Name: Список_заказаных_товаров; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public."Список_заказаных_товаров" (
    "Код_заказаных_товаров" integer NOT NULL,
    "Код_товара" integer,
    "Код_заказа" integer,
    "Кол_во_товара" integer
);


ALTER TABLE public."Список_заказаных_товаров" OWNER TO postgres;

--
-- TOC entry 205 (class 1259 OID 17298)
-- Name: Товар; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public."Товар" (
    "Код_товара" integer NOT NULL,
    "Наименование_товара" character varying(20),
    "Цена" integer
);


ALTER TABLE public."Товар" OWNER TO postgres;

--
-- TOC entry 3018 (class 0 OID 17273)
-- Dependencies: 200
-- Data for Name: Должность; Type: TABLE DATA; Schema: public; Owner: postgres
--



--
-- TOC entry 3019 (class 0 OID 17278)
-- Dependencies: 201
-- Data for Name: Заказ; Type: TABLE DATA; Schema: public; Owner: postgres
--



--
-- TOC entry 3020 (class 0 OID 17283)
-- Dependencies: 202
-- Data for Name: Клиент; Type: TABLE DATA; Schema: public; Owner: postgres
--



--
-- TOC entry 3021 (class 0 OID 17288)
-- Dependencies: 203
-- Data for Name: Сотрудники; Type: TABLE DATA; Schema: public; Owner: postgres
--



--
-- TOC entry 3022 (class 0 OID 17293)
-- Dependencies: 204
-- Data for Name: Список_заказаных_товаров; Type: TABLE DATA; Schema: public; Owner: postgres
--



--
-- TOC entry 3023 (class 0 OID 17298)
-- Dependencies: 205
-- Data for Name: Товар; Type: TABLE DATA; Schema: public; Owner: postgres
--



--
-- TOC entry 2872 (class 2606 OID 17277)
-- Name: Должность Должность_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."Должность"
    ADD CONSTRAINT "Должность_pkey" PRIMARY KEY ("Код_должности");


--
-- TOC entry 2874 (class 2606 OID 17282)
-- Name: Заказ Заказ_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."Заказ"
    ADD CONSTRAINT "Заказ_pkey" PRIMARY KEY ("Код_заказа");


--
-- TOC entry 2876 (class 2606 OID 17287)
-- Name: Клиент Клиент_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."Клиент"
    ADD CONSTRAINT "Клиент_pkey" PRIMARY KEY ("Код_клиента");


--
-- TOC entry 2878 (class 2606 OID 17292)
-- Name: Сотрудники Сотрудники_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."Сотрудники"
    ADD CONSTRAINT "Сотрудники_pkey" PRIMARY KEY ("Код_сотрудника");


--
-- TOC entry 2880 (class 2606 OID 17297)
-- Name: Список_заказаных_товаров Список_заказаных_товаров_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."Список_заказаных_товаров"
    ADD CONSTRAINT "Список_заказаных_товаров_pkey" PRIMARY KEY ("Код_заказаных_товаров");


--
-- TOC entry 2882 (class 2606 OID 17302)
-- Name: Товар Товар_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."Товар"
    ADD CONSTRAINT "Товар_pkey" PRIMARY KEY ("Код_товара");


--
-- TOC entry 2885 (class 2606 OID 17313)
-- Name: Сотрудники r_3; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."Сотрудники"
    ADD CONSTRAINT r_3 FOREIGN KEY ("Код_должности") REFERENCES public."Должность"("Код_должности");


--
-- TOC entry 2886 (class 2606 OID 17318)
-- Name: Список_заказаных_товаров r_4; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."Список_заказаных_товаров"
    ADD CONSTRAINT r_4 FOREIGN KEY ("Код_товара") REFERENCES public."Товар"("Код_товара");


--
-- TOC entry 2883 (class 2606 OID 17303)
-- Name: Заказ r_5; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."Заказ"
    ADD CONSTRAINT r_5 FOREIGN KEY ("Код_сотрудника") REFERENCES public."Сотрудники"("Код_сотрудника");


--
-- TOC entry 2884 (class 2606 OID 17308)
-- Name: Заказ r_6; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."Заказ"
    ADD CONSTRAINT r_6 FOREIGN KEY ("Код_клиента") REFERENCES public."Клиент"("Код_клиента");


--
-- TOC entry 2887 (class 2606 OID 17323)
-- Name: Список_заказаных_товаров r_7; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."Список_заказаных_товаров"
    ADD CONSTRAINT r_7 FOREIGN KEY ("Код_заказа") REFERENCES public."Заказ"("Код_заказа");


--
-- TOC entry 3029 (class 0 OID 0)
-- Dependencies: 4
-- Name: SCHEMA public; Type: ACL; Schema: -; Owner: postgres
--

REVOKE USAGE ON SCHEMA public FROM PUBLIC;
GRANT ALL ON SCHEMA public TO PUBLIC;


-- Completed on 2024-10-23 22:34:30

--
-- PostgreSQL database dump complete
--

