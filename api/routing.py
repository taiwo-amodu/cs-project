import os
import requests
import logging
from flask import Blueprint, request, jsonify
from .db import get_db_connection

# Blueprint definition
routing_bp = Blueprint('routing', __name__)

logging.basicConfig(level=logging.INFO)

api_key = os.getenv("GOOGLE_MAPS_API_KEY")

def get_nearest_service(user_lon, user_lat):
    """Finding the nearest emergency service using PostGIS."""
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
                    logging.info("No emergency services found nearby.")
                    return None
    except Exception as e:
        logging.error(f"Database query error: {e}")
        return None

def get_route_from_google(user_lon, user_lat, service_lon, service_lat):
    """Fetching route from Google Maps Directions API."""
    google_url = f"https://maps.googleapis.com/maps/api/directions/json"

    params = {
        "origin": f"{user_lat},{user_lon}",
        "destination": f"{service_lat},{service_lon}",
        "mode": "driving",  # Other modes: walking, bicycling, transit
        "key": api_key
    }

    try:
        response = requests.get(google_url, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()

        if "routes" not in data or not data["routes"]:
            return None

        # Extracting route details
        route = data["routes"][0]
        legs = route["legs"][0]

        formatted_route = {
            "distance_meters": legs["distance"]["value"],
            "duration_seconds": legs["duration"]["value"],
            "start_address": legs["start_address"],
            "end_address": legs["end_address"],
            "steps": [
                {
                    "instruction": step["html_instructions"],
                    "distance_meters": step["distance"]["value"],
                    "duration_seconds": step["duration"]["value"],
                    "start_location": step["start_location"],
                    "end_location": step["end_location"]
                }
                for step in legs["steps"]
            ],
            "polyline": route["overview_polyline"]["points"]
        }

        return formatted_route

    except requests.exceptions.RequestException as e:
        logging.error(f"Google Maps API request error: {e}")
        return None

@routing_bp.route('/api/route-to-service', methods=['GET'])
def get_route_to_service():
    """Fetching the best route from Google Maps API from user to nearest emergency service."""
    try:
        # Getting user location from request
        user_lon = request.args.get('longitude')
        user_lat = request.args.get('latitude')

        if not user_lon or not user_lat:
            return jsonify({"error": "Missing required parameters: latitude, longitude"}), 400

        try:
            user_lon, user_lat = float(user_lon), float(user_lat)
        except ValueError:
            return jsonify({"error": "Latitude and Longitude must be valid numbers"}), 400

        # Finding the nearest emergency service
        nearest_service = get_nearest_service(user_lon, user_lat)

        if not nearest_service:
            return jsonify({"error": "No emergency services found"}), 404

        # Extracting service location
        service_lon, service_lat = nearest_service["longitude"], nearest_service["latitude"]

        # Fetching route from Google Maps API
        route = get_route_from_google(user_lon, user_lat, service_lon, service_lat)

        if not route:
            return jsonify({"error": "No route found"}), 404

        formatted_response = {
            "message": "Route fetched successfully",
            "user_location": {"longitude": user_lon, "latitude": user_lat},
            "nearest_service": nearest_service,
            "route": route
        }

        return jsonify(formatted_response), 200

    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        return jsonify({"error": "Internal server error"}), 500
