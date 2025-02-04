CREATE EXTENSION IF NOT EXISTS postgis;

DROP TABLE IF EXISTS reviews;

DROP TABLE IF EXISTS emergency_services;

CREATE TABLE emergency_services (
   id SERIAL PRIMARY KEY,
   name TEXT,
   type TEXT,
   latitude DOUBLE PRECISION,
   longitude DOUBLE PRECISION,
   address TEXT,
   contact_info TEXT,
   geometry GEOMETRY
);