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
      way["amenity"="hospital"]({bbox});
      relation["amenity"="hospital"]({bbox});

      node["amenity"="police"]({bbox});
      way["amenity"="police"]({bbox});
      relation["amenity"="police"]({bbox});

      node["amenity"="fire_station"]({bbox});
      way["amenity"="fire_station"]({bbox});
      relation["amenity"="fire_station"]({bbox});
    );
    out body;
    >;
    out skel qt;
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

def calculate_centroid(geometry):
    """Calculate the centroid of a way or relation based on its geometry."""
    if not geometry:
        return None

    # Extracting latitudes and longitudes from the geometry
    try:
        lats = [point['lat'] for point in geometry if 'lat' in point]
        lons = [point['lon'] for point in geometry if 'lon' in point]
        if not lats or not lons:
            return None
        centroid_lat = sum(lats) / len(lats)
        centroid_lon = sum(lons) / len(lons)
        return {'lat': centroid_lat, 'lon': centroid_lon}
    except Exception as e:
        logger.warning(f"Error calculating centroid: {e}")
        return None

def transform_osm_data(data):
    """Transform OSM data into a list of dictionaries with relevant fields."""
    services = []
    for element in data.get('elements', []):
        service = {
            'name': element.get('tags', {}).get('name', 'Unknown'),
            'type': element.get('tags', {}).get('amenity', 'Unknown'),
            'address': element.get('tags', {}).get('addr:full', ''),
            'contact_info': element.get('tags', {}).get('phone', '')
        }

        # Handling nodes
        if element['type'] == 'node':
            service['latitude'] = element.get('lat')
            service['longitude'] = element.get('lon')

        # Handling ways and relations
        elif element['type'] in ['way', 'relation']:
            centroid = calculate_centroid(element.get('geometry', []))
            if centroid:
                service['latitude'] = centroid['lat']
                service['longitude'] = centroid['lon']
            else:
                logger.warning(f"Skipping {element['type']} {element['id']} due to missing geometry.")
                continue

        if 'latitude' in service and 'longitude' in service:
            services.append(service)

    logger.info(f"Transformed {len(services)} records.")
    return services

def load_data_to_db(services, table_name="emergency_services"):
    """Load transformed data into the PostgreSQL database."""
    # Fetching database credentials from environment variables
    dbname = os.getenv('DB_NAME', 'esl')
    user = os.getenv('DB_USER', 'postgres')
    password = os.getenv('DB_PASSWORD', 'postgres')
    host = os.getenv('DB_HOST', 'localhost')
    port = os.getenv('DB_PORT', '5432')

    try:
        with psycopg2.connect(dbname=dbname, user=user, password=password, host=host, port=port) as conn:
            with conn.cursor() as cur:
                # Inserting using PostGIS format for `location`
                execute_values(cur, f"""
                    INSERT INTO {table_name} (name, type, location, address, contact_info)
                    VALUES %s
                """, [
                    (s['name'], s['type'], 
                     f"SRID=4326;POINT({s['longitude']} {s['latitude']})", 
                     s['address'], s['contact_info'])
                    for s in services
                ])
                conn.commit()
        logger.info("Data loaded into the database successfully.")
    except psycopg2.Error as e:
        logger.error(f"Error loading data into the database: {e}")

if __name__ == "__main__":
    # Bounding box for Lisbon (south, west, north, east)
    bbox = "38.70,-9.23,38.80,-9.09"  # Fix formatting
    logger.info(f"Fetching data for Lisbon (Bounding Box: {bbox})...")

    # Extracting data from OSM
    osm_data = extract_osm_data(bbox)

    if osm_data:
        # Transforming data
        services = transform_osm_data(osm_data)

        if services:
            # Loading data into the database
            load_data_to_db(services)
        else:
            logger.warning("No services found in the transformed data.")
    else:
        logger.error("Failed to fetch data from OSM.")
