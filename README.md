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
The function get_route_from_google(user_lon, user_lat, service_lon, service_lat) sends a request to Google Maps Directions API to retrieve the best driving route.
```bash
params = {
    "origin": f"{user_lat},{user_lon}",
    "destination": f"{service_lat},{service_lon}",
    "mode": "driving",
    "key": api_key
}

response = requests.get(google_url, params=params, timeout=5)
```

## Reviews API (reviews.py)  
***Manages user-submitted reviews and ratings for emergency service locations.***   

# ESL Frontend
# Future Improvements




# Authors
James Dizon  
Justin Chung  
Taiwo Amodu

