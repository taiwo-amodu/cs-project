from flask import Blueprint, request, jsonify
from .db import get_db_connection

#make flask blueprint connection
reviews_bp = Blueprint('reviews', __name__)

#api to add reviews
@reviews_bp.route('/api/add-review', methods=['POST'])
def add_review():
    """Add a review for an emergency service."""
    #gets information from user selected service and typed information
    service_id=request.form['service_id']
    user=request.form['user_name']
    rating=request.form['rating']
    review=request.form['review']
    required_fields = [service_id,user,rating,review]

    # Validating all required fields
    for head in required_fields:
        if not head:
            return jsonify({"error": "Missing required field"}), 400

    #sql query to insert review
    sql = """INSERT INTO reviews (service_id,user_name,rating,review) VALUES (%s,%s,%s,%s);"""

    #creates database connection
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:

                # Insert review into the database
                cur.execute(sql, (service_id, user,rating,review))
                conn.commit()
                cur.close()

        return jsonify({"message": "Review added successfully"}), 201
    except Exception as e:
        return jsonify({"error": f"Failed to add review: {str(e)}"}), 500

#api to recieve reviews
@reviews_bp.route('/api/get_review', methods=['GET'])
def get_reviews():
    """Fetch reviews for a specific service."""
    #query with selected service id
    sql = """SELECT user_name, rating, review FROM reviews WHERE service_id=%s"""
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
