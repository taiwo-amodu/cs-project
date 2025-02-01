CREATE TABLE reviews (
    id SERIAL PRIMARY KEY,
    service_id INT REFERENCES emergency_services(id) ON DELETE CASCADE,
    user_name TEXT NOT NULL,
    rating INT CHECK (rating BETWEEN 1 AND 5),
    review TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
