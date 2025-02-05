This project aims to help users locate the nearest emergency services (e.g., hospitals, police stations, fire stations) based on their current location. The system will use OSM data to provide real-time information about the closest emergency services, along with details like distance, travel time, and contact information.

Project Overview
The Emergency Service Locator will be a web-based application that allows users to:
1.	Find the nearest emergency services (hospitals, police stations, fire stations, etc.) based on their current location.
2.	Get directions to the selected service using the shortest or fastest route.
3.	View additional details about the service, such as contact information, operating hours, and user reviews.
4.	Report new emergency services or update existing ones in the database.

. Technical Stack
•	Programming Language: Python 3
•	Database: PostgreSQL with PostGIS extension for spatial data handling
•	Libraries/Frameworks:
o	Flask or FastAPI for building the API
o	GeoPandas or Shapely for handling geospatial data
o	psycopg2 for interacting with PostgreSQL
o	Overpass API or OSMnx for extracting OSM data
•	Frontend (Optional): Adds-on
o	A web framework like React or Vue.js to build a user-friendly interface.
o	Integrating with a mapping library like Leaflet or Mapbox to display the results on a map.

Example Use Case
1.	A user is in an unfamiliar area and needs to find the nearest hospital.
2.	They open the Emergency Service Locator app and allow it to access their location.
3.	The app queries the database using the user’s coordinates and returns a list of nearby hospitals, sorted by distance.
4.	The user selects a hospital and views its details, including contact information and user reviews.
5.	The app provides directions to the hospital using the shortest route.



