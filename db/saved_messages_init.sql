-- Table: public.saved_messages

-- DROP TABLE IF EXISTS public.saved_messages;

CREATE TABLE IF NOT EXISTS public.saved_messages
(
    id integer NOT NULL DEFAULT nextval('saved_messages_id_seq'::regclass),
    encoded_text text COLLATE pg_catalog."default" NOT NULL,
    saved_userid integer NOT NULL,
    saved_datetime timestamp with time zone NOT NULL DEFAULT now(),
    CONSTRAINT saved_messages_pkey PRIMARY KEY (id),
    CONSTRAINT saved_messages_saved_userid_fkey FOREIGN KEY (saved_userid)
        REFERENCES public.users (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE CASCADE
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.saved_messages
    OWNER to "default";