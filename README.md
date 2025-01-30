                                                      Emergency Service locator
•	Description: A system that helps users locate the nearest emergency services (hospitals, police stations, etc.) using OSM data.

•	ETL Module: Data about emergency services from OSM will be extracted, transform to calculate distances and response times, and load into a PostgreSQL/PostGIS database.

•	CRUD Module: Users will be allowed to add or update information about emergency services.

•	API Module: An API to query the nearest emergency services based on user location using most likely postman or a simple html web interface for querying

