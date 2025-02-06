-- Create reviews table
CREATE TABLE reviews (
    id SERIAL PRIMARY KEY,
    service_id INT NOT NULL REFERENCES emergency_services(id) ON DELETE CASCADE,
    user_name VARCHAR(100) NOT NULL,
    rating INT CHECK (rating BETWEEN 1 AND 5),
    review TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index on `service_id` to improve lookup performance
CREATE INDEX idx_reviews_service_id ON reviews(service_id);

-- Optional: Index on `rating` if frequent rating-based queries are expected
CREATE INDEX idx_reviews_rating ON reviews(rating);