from flask import Blueprint, request, jsonify
from api.db import get_db_connection

reviews_bp = Blueprint('reviews', __name__)

@reviews_bp.route('/api/add-review', methods=['POST'])
def add_review():
    """Add a review for an emergency service."""
    data = request.json
    required_fields = ['service_id', 'user_name', 'rating', 'review']

    if not all(field in data for field in required_fields) or not (1 <= data['rating'] <= 5):
        return jsonify({"error": "Invalid input"}), 400

    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500

    try:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO reviews (service_id, user_name, rating, review)
                VALUES (%s, %s, %s, %s);
            """, (data['service_id'], data['user_name'], data['rating'], data['review']))
            conn.commit()
        return jsonify({"message": "Review added successfully"}), 201
    except Exception as e:
        return jsonify({"error": f"Failed to add review: {e}"}), 500
    finally:
        conn.close()


@reviews_bp.route('/api/reviews/<int:service_id>', methods=['GET'])
def get_reviews(service_id):
    """Fetch reviews for a specific service."""
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                # Fetch reviews
                cur.execute("SELECT id, service_id, user_name, rating, review FROM reviews WHERE service_id = %s", (service_id,))
                columns = [desc[0] for desc in cur.description]  # Get column names
                reviews = [dict(zip(columns, row)) for row in cur.fetchall()]  # Convert to JSON

        if not reviews:
            return jsonify({"message": "No reviews found for this service"}), 404

        return jsonify(reviews), 200
    except Exception as e:
        return jsonify({"error": f"Failed to fetch reviews: {str(e)}"}), 500
