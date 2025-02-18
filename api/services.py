from flask import Blueprint, request, jsonify
from .db import get_db_connection
from geopy.distance import geodesic

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

@services_bp.route('/api/search-services', methods=['GET'])
def search_services():
    """Find services by type and within a given radius using GEOMETRY."""
    service_type = request.args.get('type')
    user_lat = request.args.get('lat')
    user_lng = request.args.get('lng')
    radius_km = request.args.get('radius', 2)  # Default 2km

    if not service_type or not user_lat or not user_lng:
        return jsonify({"error": "Missing parameters (type, lat, lng)"}), 400

    try:
        user_lat, user_lng = float(user_lat), float(user_lng)
        radius_m = float(radius_km) * 1000  # Convert km to meters

        conn = get_db_connection()
        cur = conn.cursor()

        # Query using ST_DWithin to find services within radius
        cur.execute("""
            SELECT 
                id, 
                name, 
                type, 
                address, 
                contact_info, 
                ST_AsText(location) AS location
            FROM emergency_services 
            WHERE type = %s
            AND ST_DWithin(
                location, 
                ST_SetSRID(ST_MakePoint(%s, %s), 4326), 
                %s
            );
        """, (service_type, user_lng, user_lat, radius_m))

        services = cur.fetchall()
        cur.close()
        conn.close()

        # Convert results into JSON format
        nearby_services = []
        for s in services:
            geo_point = s[5].replace("POINT(", "").replace(")", "").split()
            service_lng, service_lat = map(float, geo_point)

            nearby_services.append({
                "id": s[0], "name": s[1], "type": s[2], "address": s[3], "contact_info": s[4],
                "latitude": service_lat, "longitude": service_lng
            })

        return jsonify(nearby_services)

    except Exception as e:
        return jsonify({"error": str(e)}), 500
