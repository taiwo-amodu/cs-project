from flask import Blueprint, request, jsonify
from api.db import get_db_connection

services_bp = Blueprint('services', __name__)

@services_bp.route('/api/services', methods=['GET'])
def get_services():
    """Fetch all emergency services with review count."""
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT id, name, type, latitude, longitude, contact_info FROM emergency_services")
                columns = [desc[0] for desc in cur.description]  # Get column names
                services = [dict(zip(columns, row)) for row in cur.fetchall()]  # Convert to dict

        if not services:
            return jsonify({"message": "No emergency services found"}), 404

        return jsonify(services), 200
    except Exception as e:
        return jsonify({"error": f"Failed to fetch services: {str(e)}"}), 500


@services_bp.route('/api/add-service', methods=['POST'])
def add_service():
    """Add a new emergency service."""
    data = request.json
    required_fields = ['name', 'type', 'latitude', 'longitude', 'address', 'contact_info']

    # Validate all required fields
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400

    # Validate latitude and longitude
    try:
        lat, lon = float(data['latitude']), float(data['longitude'])
    except ValueError:
        return jsonify({"error": "Latitude and Longitude must be numbers"}), 400

    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO emergency_services (name, type, latitude, longitude, address, contact_info)
                    VALUES (%s, %s, %s, %s, %s, %s);
                """, (data['name'], data['type'], lat, lon, data['address'], data['contact_info']))
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
                # Check if the service exists
                cur.execute("SELECT * FROM emergency_services WHERE id = %s", (service_id,))
                service = cur.fetchone()
                
                if not service:
                    return jsonify({"error": "Service not found"}), 404

                # Delete the service
                cur.execute("DELETE FROM emergency_services WHERE id = %s", (service_id,))
                conn.commit()

        return jsonify({"message": f"Service with ID {service_id} deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": f"Failed to delete service: {str(e)}"}), 500
