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
- Integrating with a mapping library like Mapbox to display the results on a map.

# Example Use Case
1. A user is unfamiliar with the area and needs to find the nearest emergency service.
2. They open the ESL app and allow it to access their location.
3. The app queries the database using the user’s coordinates and returns a list of nearby hospitals, sorted by distance.
4. The user selects an emergency service and views its details, including contact information and user reviews.
5. The app provides directions to the chosen service using the shortest route.

# Data Extraction
We extracted emergency service locations from OpenStreetMap (OSM) using the Overpass API, focusing on key amenities such as hospitals, fire stations, and police stations. The extracted data, filtered by relevant OSM tags, was obtained in GeoJSON format and processed through an ETL pipeline. This involved transforming the data into a PostGIS-compatible format and loading it into a PostgreSQL/PostGIS database for efficient spatial queries.  

To ensure data quality, we cleaned and standardized the service names, addresses, and geographic coordinates. The backend API interacts with this database to dynamically find the nearest emergency service to a user’s location and retrieve a route using the Google Maps Directions API for navigation. This integration enables real-time emergency service location and routing based on user input. 
# Database
We use PostgreSQL with PostGIS to store and manage emergency service locations. The database contains structured data on hospitals, fire stations, and police stations, with attributes such as name, type, contact information, and geographic coordinates. PostGIS enables spatial queries, allowing us to efficiently find the nearest service based on the user’s location.
# ETL
Our ETL pipeline uses the Overpass API to extract emergency service data from OSM. The extracted data is transformed into a PostGIS-compatible format, ensuring consistency in attributes like names and addresses. We then clean the data by filtering relevant points of interest (POIs) and validating geographic coordinates before loading them into our database for efficient spatial querying.
# API
# ESL Frontend




# Authors
James Dizon  
Justin Chung  
Taiwo Amodu

