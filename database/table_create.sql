CREATE TABLE emergency_services (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    type VARCHAR(50) NOT NULL,
    latitude FLOAT NOT NULL,
    longitude FLOAT NOT NULL,
    address TEXT,
    contact_info VARCHAR(100)
);

CREATE TABLE comments(
    id PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    comment TEXT,
    stars INT,
    building_id FOREIGN KEY
)