import requests
import psycopg2
from psycopg2.extras import execute_values
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def extract_osm_data(bbox):
    """Fetch emergency services data from OpenStreetMap using the Overpass API for a bounding box."""
    overpass_url = "http://overpass-api.de/api/interpreter"
    query = f"""
    [out:json];
    (
      node["amenity"="hospital"]({bbox});
      node["amenity"="police"]({bbox});
      node["amenity"="fire_station"]({bbox});
    );
    out body;
    """
    try:
        logger.info("Fetching data from Overpass API...")
        response = requests.get(overpass_url, params={'data': query})
        response.raise_for_status()  # Raise an error for bad status codes
        data = response.json()
        logger.info("Data fetched successfully.")
        return data
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching data from Overpass API: {e}")
        return None

def transform_osm_data(data):
    """Transform OSM data into a list of dictionaries with relevant fields."""
    services = []
    for element in data['elements']:
        service = {
            'name': element.get('tags', {}).get('name', 'Unknown'),
            'type': element.get('tags', {}).get('amenity', 'Unknown'),
            'latitude': element.get('lat'),
            'longitude': element.get('lon'),
            'address': element.get('tags', {}).get('addr:full', ''),
            'contact_info': element.get('tags', {}).get('phone', '')
        }
        services.append(service)
    logger.info(f"Transformed {len(services)} records.")
    return services

def load_data_to_db(services):
    """Load transformed data into the PostgreSQL database."""
    # Fetch database credentials from environment variables
    dbname = os.getenv('DB_NAME', 'emergency_services')
    user = os.getenv('DB_USER', 'your_username')
    password = os.getenv('DB_PASSWORD', 'your_password')
    host = os.getenv('DB_HOST', 'localhost')

    try:
        # Use a context manager for database connection
        with psycopg2.connect(dbname=dbname, user=user, password=password, host=host) as conn:
            with conn.cursor() as cur:
                # Use batch insertion for better performance
                execute_values(cur, """
                    INSERT INTO emergency_services (name, type, latitude, longitude, address, contact_info)
                    VALUES %s
                """, [(s['name'], s['type'], s['latitude'], s['longitude'], s['address'], s['contact_info']) for s in services])
                conn.commit()
        logger.info("Data loaded into the database successfully.")
    except psycopg2.Error as e:
        logger.error(f"Error loading data into the database: {e}")

if __name__ == "__main__":
    # Bounding box for Lisbon (south, west, north, east)
    bbox = "38.70, -9.23, 38.80, -9.09"
    logger.info(f"Fetching data for Lisbon (Bounding Box: {bbox})...")
    
    # Extract data from OSM
    osm_data = extract_osm_data(bbox)
    
    if osm_data:
        # Transform data
        services = transform_osm_data(osm_data)
        
        if services:
            # Load data into the database
            load_data_to_db(services)
        else:
            logger.warning("No services found in the transformed data.")
    else:
        logger.error("Failed to fetch data from OSM.")