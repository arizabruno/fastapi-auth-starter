create table public.users
(
    user_id         serial,
    email           varchar(255) default 'guest@namex.com'::character varying,
    username        varchar(255) default 'guest'::character varying not null,
    hashed_password varchar(255),
    roles          text      default "user"                      not null,
    created_at      timestamp    default now()
);

alter table public.users
    owner to aziradev;
