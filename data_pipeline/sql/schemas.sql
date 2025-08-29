-- Schémas
CREATE SCHEMA IF NOT EXISTS bronze;
CREATE SCHEMA IF NOT EXISTS silver;
CREATE SCHEMA IF NOT EXISTS gold;

-- Bronze
CREATE TABLE IF NOT EXISTS bronze.arcep_raw (
  load_id          uuid        NOT NULL,
  load_ts          timestamptz NOT NULL DEFAULT now(),
  source_file      text        NOT NULL,
  "EZABPQM"        text,
  "Tranche_Debut"  text,
  "Tranche_Fin"    text,
  "Mnémo"          text,
  "Territoire"     text,
  "Date_Attribution" text
);

-- Silver
CREATE TABLE IF NOT EXISTS silver.arcep_clean (
  load_id          uuid        NOT NULL,
  ezabpqm          varchar     NOT NULL,
  tranche_debut    bigint      NOT NULL,
  tranche_fin      bigint      NOT NULL,
  mnemo            varchar     NOT NULL,
  territoire       text        NOT NULL,
  date_attribution date        NOT NULL,
  PRIMARY KEY (ezabpqm, tranche_debut, tranche_fin)
);

-- Gold
CREATE TABLE IF NOT EXISTS gold.arcep_summary (
  ezabpqm          varchar     NOT NULL,  
  mnemo            varchar     NOT NULL,
  tranche_debut    bigint      NOT NULL,
  tranche_fin      bigint      NOT NULL,
  last_update      timestamptz NOT NULL DEFAULT now(),
  PRIMARY KEY (ezabpqm, tranche_debut, tranche_fin)
);