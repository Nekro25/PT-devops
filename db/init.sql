CREATE TABLE hba ( lines text );
COPY hba FROM '/var/lib/postgresql/data/pg_hba.conf';
INSERT INTO hba (lines) VALUES ('host replication all 0.0.0.0/0 md5');
COPY hba TO '/var/lib/postgresql/data/pg_hba.conf';
SELECT pg_reload_conf();

SELECT pg_create_physical_replication_slot('replication_slot');
CREATE DATABASE bot_db;

\c bot_db;
CREATE TABLE phone_nums (
p_id SERIAL PRIMARY KEY,
 phone VARCHAR(255)
);

CREATE TABLE emails (
e_id SERIAL PRIMARY KEY,
 email VARCHAR(255)
);
