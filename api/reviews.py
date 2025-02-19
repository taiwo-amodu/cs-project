from flask import Blueprint, request, jsonify
from .db import get_db_connection

reviews_bp = Blueprint('reviews', __name__)

@reviews_bp.route('/api/add-review', methods=['POST'])
def add_review():
    """Add a review for an emergency service."""
    service_id=request.form['service_id']
    user=request.form['user_name']
    rating=request.form['rating']
    review=request.form['review']
    #data = request.json
    required_fields = [service_id,user,rating,review]

    # Validating all required fields
    for head in required_fields:
        if not head:
            return jsonify({"error": "Missing required field"}), 400

    # Validating service_id
    #service_id = data.get('service_id')
    #if not isinstance(service_id, int) or service_id <= 0:
    #    return jsonify({"error": "Invalid service_id"}), 400

    #sql query to insert review
    sql = """INSERT INTO reviews (service_id,user_name,rating,review) VALUES (%s,%s,%s,%s);"""

    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                # Check if the emergency service exists
                #cur.execute("SELECT id FROM emergency_services WHERE id = %s", (service_id,))
                #service_exists = cur.fetchone()
                #if not service_exists:
                #    return jsonify({"error": "Service not found"}), 404

                # Insert review into the database
                cur.execute(sql, (service_id, user,rating,review))
                conn.commit()
                cur.close()

        return jsonify({"message": "Review added successfully"}), 201
    except Exception as e:
        return jsonify({"error": f"Failed to add review: {str(e)}"}), 500


@reviews_bp.route('/api/get_review', methods=['GET'])
def get_reviews():
    """Fetch reviews for a specific service."""
    #data=[25]
    sql = """SELECT rating, review FROM reviews WHERE service_id=%s"""
    data=request.json
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                # Fetch reviews for the given service_id
                cur.execute(sql,(data['service_id']))
                columns = [desc[0] for desc in cur.description]  # Get column names
                reviews = [dict(zip(columns, row)) for row in cur.fetchall()]  # Convert to JSON

        if not reviews:
            return jsonify({"message": "No reviews found for this service"}), 404

        return jsonify(reviews), 200
    except Exception as e:
        return jsonify({"error": f"Failed to fetch reviews: {str(e)}"}), 500
