import requests
from flask import Blueprint, request, jsonify
from .db import get_db_connection

routing_bp = Blueprint('routing', __name__)

def get_nearest_service(user_lon, user_lat):
    """Find the nearest emergency service using PostGIS."""
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT id, name, type, address, contact_info,
                           ST_X(location::geometry) AS longitude, 
                           ST_Y(location::geometry) AS latitude,
                           ST_Distance(location, ST_SetSRID(ST_MakePoint(%s, %s), 4326)) AS distance
                    FROM emergency_services
                    ORDER BY distance ASC
                    LIMIT 1;
                """, (user_lon, user_lat))

                result = cur.fetchone()
                if result:
                    return {
                        "id": result[0],
                        "name": result[1],
                        "type": result[2],
                        "address": result[3],
                        "contact_info": result[4],
                        "longitude": result[5],
                        "latitude": result[6],
                        "distance_meters": result[7]
                    }
                else:
                    return None
    except Exception as e:
        return None

@routing_bp.route('/api/route-to-service', methods=['GET'])
def get_route_to_service():
    """Fetch the best route from the user's live location to the nearest emergency service."""
    try:
        # Get user location from request
        user_lon = request.args.get('longitude')
        user_lat = request.args.get('latitude')

        if not user_lon or not user_lat:
            return jsonify({"error": "Missing required parameters: latitude, longitude"}), 400

        try:
            user_lon, user_lat = float(user_lon), float(user_lat)
        except ValueError:
            return jsonify({"error": "Latitude and Longitude must be valid numbers"}), 400

        # Find the nearest emergency service
        nearest_service = get_nearest_service(user_lon, user_lat)

        if not nearest_service:
            return jsonify({"error": "No emergency services found"}), 404

        # Extract service location
        service_lon, service_lat = nearest_service["longitude"], nearest_service["latitude"]

        # OSRM Routing API request
        osrm_url = f"http://router.project-osrm.org/route/v1/driving/{user_lon},{user_lat};{service_lon},{service_lat}?overview=full&steps=true"
        response = requests.get(osrm_url)
        response.raise_for_status()

        data = response.json()

        if "routes" not in data or not data["routes"]:
            return jsonify({"error": "No route found"}), 404

        # Extract route details
        route = data["routes"][0]

        formatted_response = {
            "message": "Route fetched successfully",
            "user_location": {"longitude": user_lon, "latitude": user_lat},
            "nearest_service": nearest_service,
            "route": {
                "distance_meters": route["distance"],
                "duration_seconds": route["duration"],
                "geometry": route["geometry"],
                "steps": [
                    {
                        "instruction": step["maneuver"].get("instruction", "No instruction available"),
                        "location": step["maneuver"]["location"],
                        "duration": step["duration"],
                        "distance": step["distance"]
                    }
                    for leg in route["legs"] for step in leg.get("steps", [])
                ]
            }
        }

        return jsonify(formatted_response), 200

    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Failed to fetch route: {str(e)}"}), 500
