-- Table: public.users

-- DROP TABLE IF EXISTS public.users;

CREATE TABLE IF NOT EXISTS public.users
(
    id integer NOT NULL DEFAULT nextval('users_id_seq'::regclass),
    username text COLLATE pg_catalog."default" NOT NULL,
    password text COLLATE pg_catalog."default" NOT NULL,
    first_name text COLLATE pg_catalog."default",
    last_name text COLLATE pg_catalog."default",
    email text COLLATE pg_catalog."default",
    creation_datetime timestamp with time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_modified_datetime timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    creation_userid text COLLATE pg_catalog."default" NOT NULL DEFAULT 'system'::text,
    last_modified_userid text COLLATE pg_catalog."default" DEFAULT 'system'::text,
    sso text COLLATE pg_catalog."default",
    CONSTRAINT users_pkey PRIMARY KEY (id),
    CONSTRAINT users_email_key UNIQUE (email),
    CONSTRAINT users_username_key UNIQUE (username)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.users
    OWNER to "default";