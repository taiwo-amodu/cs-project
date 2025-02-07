from flask import Blueprint, request, jsonify
from .db import get_db_connection

services_bp = Blueprint('services', __name__)

@services_bp.route('/api/services', methods=['GET'])
def get_services():
    """Fetch all emergency services with geometry correctly extracted."""
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT id, name, type, 
                           ST_X(location::geometry) AS longitude, 
                           ST_Y(location::geometry) AS latitude, 
                           address, contact_info 
                    FROM emergency_services;
                """)
                columns = [desc[0] for desc in cur.description]
                services = [dict(zip(columns, row)) for row in cur.fetchall()]

        if not services:
            return jsonify({"message": "No emergency services found"}), 404

        return jsonify(services), 200
    except Exception as e:
        return jsonify({"error": f"Failed to fetch services: {str(e)}"}), 500


@services_bp.route('/api/add-service', methods=['POST'])
def add_service():
    """Add a new emergency service with PostGIS location storage."""
    data = request.json
    required_fields = ['name', 'type', 'latitude', 'longitude', 'address', 'contact_info']

    # Validating required fields
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400

    try:
        # Validating latitude & longitude
        lat, lon = float(data['latitude']), float(data['longitude'])
    except ValueError:
        return jsonify({"error": "Latitude and Longitude must be valid numbers"}), 400

    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                # Inserting location as PostGIS GEOGRAPHY(POINT, 4326)
                cur.execute("""
                    INSERT INTO emergency_services (name, type, location, address, contact_info)
                    VALUES (%s, %s, ST_SetSRID(ST_MakePoint(%s, %s), 4326), %s, %s);
                """, (data['name'], data['type'], lon, lat, data['address'], data['contact_info']))
                conn.commit()

        return jsonify({"message": "Service added successfully"}), 201
    except Exception as e:
        return jsonify({"error": f"Failed to add service: {str(e)}"}), 500



@services_bp.route('/api/delete-service/<int:service_id>', methods=['DELETE'])
def delete_service(service_id):
    """Delete an emergency service by ID."""
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                # Checking if the service exists
                cur.execute("SELECT * FROM emergency_services WHERE id = %s", (service_id,))
                service = cur.fetchone()
                
                if not service:
                    return jsonify({"error": "Service not found"}), 404

                # Deleting the service
                cur.execute("DELETE FROM emergency_services WHERE id = %s", (service_id,))
                conn.commit()

        return jsonify({"message": f"Service with ID {service_id} deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": f"Failed to delete service: {str(e)}"}), 500
