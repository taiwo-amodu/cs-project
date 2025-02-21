# Emergency Service Locator (ESL)

This project aims to help users locate the nearest emergency services (e.g., hospitals, police stations, fire stations) based on their current location. The system will use OSM data to provide real-time information about the closest emergency services and details like distance, travel time, and contact information.

# Project Overview
The ESL will be a web-based application that allows users to:  
- Find the nearest emergency services (hospitals, police stations, fire stations, etc.) based on their current location.  
- Get directions to the selected service using the shortest or fastest route.  
- View additional details about the service, such as contact information, operating hours, and user reviews.  
- Report new emergency services or update existing ones in the database.  

# Technical Stack
- Programming Language: Python 3
- Database: PostgreSQL with PostGIS extension for spatial data handling
- Libraries/Frameworks:
- Flask  for building the API
- GeoPandas for handling geospatial data
- psycopg2 for interacting with PostgreSQL
- Overpass API or OSMnx for extracting OSM data
- Frontend: Google Maps API
- A web framework like HTML to build a user-friendly interface.
- Integrating with a mapping library like Google maps to display the results on a map.

# Example Use Case
1. A user is unfamiliar with the area and needs to find the nearest emergency service.
2. They open the ESL app and allow it to access their location.
3. The app queries the database using the user’s coordinates and returns a list of nearby hospitals, sorted by distance.
4. The user selects an emergency service and views its details, including contact information and user reviews.
5. The app provides directions to the chosen service using the shortest route.

# Data Extraction
Emergency service locations were extracted from OpenStreetMap (OSM) using the Overpass API, focusing on key amenities such as hospitals, fire stations, and police stations. The extracted data, filtered by relevant OSM tags, was obtained in GeoJSON format and processed through an ETL pipeline. This involved transforming the data into a PostGIS-compatible format and loading it into a PostgreSQL/PostGIS database for efficient spatial queries.  

To ensure data quality, we cleaned and standardized the service names, addresses, and geographic coordinates. The backend API interacts with this database to dynamically find the nearest emergency service to a user’s location and retrieve a route using the Google Maps Directions API for navigation. This integration enables real-time emergency service location and routing based on user input. 
# Database
PostgreSQL with PostGIS was used to create the database for this project, which stores and manages emergency service locations. The database contains structured data on hospitals, fire stations, and police stations, with attributes such as name, type, contact information, and geographic coordinates. PostGIS enables spatial queries, allowing us to efficiently find the nearest service based on the user’s location.
# ETL
The ETL pipeline uses the Overpass API to extract emergency service data from OSM. The extracted data is transformed into a PostGIS-compatible format, ensuring consistency in attributes like names and addresses. We then clean the data by filtering relevant points of interest (POIs) and validating geographic coordinates before loading them into our database for efficient spatial querying.
# API
The API was divided into three parts: **Services**, **Routing**, and **Reviews** to keep the backend structured and manageable.  
## Services API (services.py) 
***Handles emergency service locations, fetching details such as hospitals, police stations, and fire stations from a database.***  

**Fetching All Emergency Services**  
Retrieves all available emergency services from the database. Uses PostGIS functions ST_X() and ST_Y() to extract latitude and longitude from the GEOMETRY column and returns a JSON array containing all services.
```bash
@services_bp.route('/api/add-service', methods=['POST'])
def add_service():
    """Add a new emergency service with PostGIS location storage."""
    data = request.json
    required_fields = ['name', 'type', 'latitude', 'longitude', 'address', 'contact_info']

    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400

    try:
        lat, lon = float(data['latitude']), float(data['longitude'])
    except ValueError:
        return jsonify({"error": "Latitude and Longitude must be valid numbers"}), 400

    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO emergency_services (name, type, location, address, contact_info)
                    VALUES (%s, %s, ST_SetSRID(ST_MakePoint(%s, %s), 4326), %s, %s);
                """, (data['name'], data['type'], lon, lat, data['address'], data['contact_info']))
                conn.commit()

        return jsonify({"message": "Service added successfully"}), 201
    except Exception as e:
        return jsonify({"error": f"Failed to add service: {str(e)}"}), 500
```
**Adding a New Emergency Service**  
Adds a new emergency service, storing its location as a PostGIS point. Uses ST_SetSRID(ST_MakePoint(lon, lat), 4326) to store location as a GEOMETRY point, ensures all required fields are present and valid and returns a 201 Created response on success.
```bash
@services_bp.route('/api/add-service', methods=['POST'])
def add_service():
    """Add a new emergency service with PostGIS location storage."""
    data = request.json
    required_fields = ['name', 'type', 'latitude', 'longitude', 'address', 'contact_info']

    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400

    try:
        lat, lon = float(data['latitude']), float(data['longitude'])
    except ValueError:
        return jsonify({"error": "Latitude and Longitude must be valid numbers"}), 400

    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO emergency_services (name, type, location, address, contact_info)
                    VALUES (%s, %s, ST_SetSRID(ST_MakePoint(%s, %s), 4326), %s, %s);
                """, (data['name'], data['type'], lon, lat, data['address'], data['contact_info']))
                conn.commit()

        return jsonify({"message": "Service added successfully"}), 201
    except Exception as e:
        return jsonify({"error": f"Failed to add service: {str(e)}"}), 500
```
**Deleting a Service by ID**  
Deletes a specific emergency service by its ID. First, it checks if the service exists before deletion and then deletes the service if found and returns a 200 OK response.
```bash
@services_bp.route('/api/delete-service/<int:service_id>', methods=['DELETE'])
def delete_service(service_id):
    """Delete an emergency service by ID."""
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM emergency_services WHERE id = %s", (service_id,))
                service = cur.fetchone()
                
                if not service:
                    return jsonify({"error": "Service not found"}), 404

                cur.execute("DELETE FROM emergency_services WHERE id = %s", (service_id,))
                conn.commit()

        return jsonify({"message": f"Service with ID {service_id} deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": f"Failed to delete service: {str(e)}"}), 500
```
**Searching for Services by Type & Proximity**  
Finds nearby emergency services of a specified type within a given radius. Uses ST_DWithin(location, ST_SetSRID(ST_MakePoint(lon, lat), 4326), radius_m) to find nearby services. Filters results by service type and returns a JSON list of emergency services within the specified radius.
```bash
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
```
## Routing API (routing.py) 
***Provides route calculations to help users navigate to the nearest emergency service.***  

The routing_bp blueprint is created to handle routing-related API endpoints.
```bash
routing_bp = Blueprint('routing', __name__)
```
The function get_nearest_service(user_lon, user_lat) queries the PostgreSQL database using PostGIS to find the closest emergency service. Uses ST_Distance to calculate the distance between the user and each service.  Orders result by distance and return the closest service.
```bash
cur.execute("""
    SELECT id, name, type, address, contact_info,
           ST_X(location::geometry) AS longitude, 
           ST_Y(location::geometry) AS latitude,
           ST_Distance(location, ST_SetSRID(ST_MakePoint(%s, %s), 4326)) AS distance
    FROM emergency_services
    ORDER BY distance ASC
    LIMIT 1;
""", (user_lon, user_lat))
```
The function get_route_from_google(user_lon, user_lat, service_lon, service_lat) sends a request to Google Maps Directions API to retrieve the best driving route. It extracts and formats polylines to visualize the route.
```bash
params = {
    "origin": f"{user_lat},{user_lon}",
    "destination": f"{service_lat},{service_lon}",
    "mode": "driving",
    "key": api_key
}

response = requests.get(google_url, params=params, timeout=5)
```
API Endpoint: /api/route-to-service
- Receives latitude and longitude from the user.  
- Calls get_nearest_service() to find the closest emergency service.  
- Calls get_route_from_google() to get directions.  
- Returns a structured JSON response.  
```bash
@routing_bp.route('/api/route-to-service', methods=['GET'])
def get_route_to_service():
    user_lon = request.args.get('longitude')
    user_lat = request.args.get('latitude')

    if not user_lon or not user_lat:
        return jsonify({"error": "Missing required parameters: latitude, longitude"}), 400

    nearest_service = get_nearest_service(float(user_lon), float(user_lat))

    if not nearest_service:
        return jsonify({"error": "No emergency services found"}), 404

    route = get_route_from_google(float(user_lon), float(user_lat),
                                  nearest_service["longitude"], nearest_service["latitude"])

    if not route:
        return jsonify({"error": "No route found"}), 404

    return jsonify({
        "message": "Route fetched successfully",
        "user_location": {"longitude": user_lon, "latitude": user_lat},
        "nearest_service": nearest_service,
        "route": route
    }), 200
```
## Reviews API (reviews.py)  
***Manages user-submitted reviews and ratings for emergency service locations.***   

# ESL Frontend
This is the frontend of the Emergenceny Service Locator. Several buttons can be foun in the top left corner where users can click on the "Find my Location" button to show their current location in the map. A dropdown list can also be found which shows the list of the service types and the users can select which type of service they are looking for. After selecting the service type the users can click "Serach Nearby" button to see the location of the nearest services in their current location.
![image](https://github.com/user-attachments/assets/9af3fe71-c2b8-4b9b-adc2-6120e18b3133)
![image](https://github.com/user-attachments/assets/b2190dc3-0406-44d8-8034-d5ef7c210e9c)  

When a user selects a service a route going to the service will be shown in the map and the relevant details about the selected service. Users can also submit a review about the service that they have selected.
![image](https://github.com/user-attachments/assets/a9b1d933-b4f0-4a4a-a326-abc5036a539c)
![image](https://github.com/user-attachments/assets/d464bb20-cc4b-492e-8ef3-153adb04ef4c)

# Future Improvements
- Include information on service availability, such as 24/7 emergency response or limited hours of operation, and other relevant information that can help the users.  
- Allow filtering by multiple criteria such as service type, availability, or distance.  
- Include a list of services and rank based on distance, user ratings, or urgency level.  
- Allow users to save frequently used services and get personalized recommendations.  




# Authors
James Dizon  
Justin Chung  
Taiwo Amodu

