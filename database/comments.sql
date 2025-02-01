CREATE TABLE comments (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    comment TEXT,
    stars INT,
    building_id INT,
    FOREIGN KEY (id) REFERENCES emergency_services(id)
);