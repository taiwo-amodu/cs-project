import psycopg2
import os
import logging
from dotenv import load_dotenv

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)

def get_db_connection():
    """Establish a connection to the PostgreSQL database."""
    try:
        conn = psycopg2.connect(
            dbname=os.getenv('DB_NAME'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            host=os.getenv('DB_HOST'),
            port=os.getenv('DB_PORT')
        )
        logging.info("✅ Database connection successful")
        return conn
    except psycopg2.OperationalError as e:
        logging.error(f"❌ Database connection failed: {e}")
        raise RuntimeError("Database connection failed") from e  # Raise error instead of returning None

if __name__ == "__main__":
    get_db_connection()






# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)

# def get_db_connection():
#     """Establish a connection to the PostgreSQL database."""
#     try:
#         conn = psycopg2.connect(
#             dbname=os.getenv('DB_NAME'),
#             user=os.getenv('DB_USER'),
#             password=os.getenv('DB_PASSWORD'),
#             host=os.getenv('DB_HOST'),
#             port=os.getenv('DB_PORT')
#         )
#         logging.info("✅ Database connection successful")
#         return conn
#     except psycopg2.OperationalError as e:
#         logging.error(f"❌ Database connection failed: {e}")
#         print(f"❌ Database connection failed: {e}")  # <-- This will show the actual error
#         raise  # <-- Let the script print the actual error without wrapping it in RuntimeError

# # Test the connection
# if __name__ == "__main__":
#     get_db_connection()

# import os
# from dotenv import load_dotenv

# # Explicitly load .env from the current directory
# dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
# load_dotenv(dotenv_path=dotenv_path)

# # Print variables to confirm they are loaded
# print("DB_USER:", os.getenv("DB_USER"))
# print("DB_NAME:", os.getenv("DB_NAME"))
# print("DB_HOST:", os.getenv("DB_HOST"))
# print("DB_PORT:", os.getenv("DB_PORT"))

