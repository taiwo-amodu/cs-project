import requests
from flask import Blueprint, request, jsonify

routing_bp = Blueprint('routing', __name__)

@routing_bp.route('/api/route', methods=['GET'])
def get_route():
    """Fetch a route between two points using OSRM."""
    try:
        # Get query parameters
        start_lon = request.args.get('start_lon')
        start_lat = request.args.get('start_lat')
        end_lon = request.args.get('end_lon')
        end_lat = request.args.get('end_lat')

        # Validate inputs
        try:
            start_lon, start_lat = float(start_lon), float(start_lat)
            end_lon, end_lat = float(end_lon), float(end_lat)
        except (ValueError, TypeError):
            return jsonify({"error": "Invalid coordinates. Please provide numeric values."}), 400

        osrm_url = f"http://router.project-osrm.org/route/v1/driving/{start_lon},{start_lat};{end_lon},{end_lat}?overview=full"

        # Make request to OSRM
        response = requests.get(osrm_url)
        response.raise_for_status()  # Raise an error for HTTP issues

        data = response.json()
        
        # Check if OSRM returned a valid route
        if "routes" not in data or not data["routes"]:
            return jsonify({"error": "No route found"}), 404

        # Extract important details
        route = data["routes"][0]
        waypoints = data["waypoints"]

        formatted_response = {
            "message": "Route fetched successfully",
            "distance_meters": route["distance"],
            "duration_seconds": route["duration"],
            "start_location": {"longitude": waypoints[0]["location"][0], "latitude": waypoints[0]["location"][1]},
            "end_location": {"longitude": waypoints[1]["location"][0], "latitude": waypoints[1]["location"][1]},
            "geometry": route["geometry"],  # Encoded polyline for the route
        }

        return jsonify(formatted_response), 200

    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Failed to fetch route: {str(e)}"}), 500
