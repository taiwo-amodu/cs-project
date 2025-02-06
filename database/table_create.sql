-- Enable PostGIS extension
CREATE EXTENSION IF NOT EXISTS postgis;

-- Create emergency_services table
CREATE TABLE emergency_services (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    type VARCHAR(50) NOT NULL,
    location GEOGRAPHY(POINT, 4326) NOT NULL,
    address TEXT,
    contact_info VARCHAR(150)
);

-- Create an index on the spatial column for optimized spatial queries
CREATE INDEX emergency_services_location_idx ON emergency_services USING GIST (location);
