import os
import random
import json
import requests
from flask import Flask, request, jsonify, session
from flask_cors import CORS
from kafka import KafkaProducer
from werkzeug.security import generate_password_hash, check_password_hash
from google.cloud import bigquery
from dotenv import load_dotenv
import logging
import threading
from kafka import KafkaConsumer
from google.oauth2 import service_account
from google.cloud import bigquery
import sqlalchemy

# SQLAlchemy and Cloud SQL Connector
from google.cloud.sql.connector import Connector, IPTypes
# import pymysql
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Load environment variables
load_dotenv()

# Flask app setup
app = Flask(__name__)
app.secret_key = os.urandom(24)  # For secure session management
CORS(app)


producer = KafkaProducer(
    bootstrap_servers=['IP OF THE KAFKA SERVERS'],  # EXTERNAL listener
    security_protocol="SASL_PLAINTEXT",       # Required protocol
    sasl_mechanism="PLAIN",                   # SASL mechanism
    sasl_plain_username="",             # Username from config
    sasl_plain_password="",        # Password from config
    value_serializer=lambda v: json.dumps(v).encode('utf-8'),  # JSON serialization
)
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def start_kafka_consumer():
    try:
        # Set up BigQuery client
        client = bigquery.Client(credentials=service_account.Credentials.from_service_account_file('credentials_temp.json'))
        table_id = ''  # bigquery table id 


        # Set up Kafka Consumer
        consumer = KafkaConsumer(
            'news_data',
            bootstrap_servers=['IP OF THE KAFKA SERVERS'],
            group_id='backend_consumer_group',
            security_protocol="SASL_PLAINTEXT",          # Required protocol
    sasl_mechanism="PLAIN",                      # SASL mechanism
    sasl_plain_username="",                 # Username from broker config
    sasl_plain_password="",            # Password from broker config
    auto_offset_reset='earliest',                # Start from the earliest message               # Consumer group ID
    value_deserializer=lambda v: json.loads(v.decode('utf-8'))  # Deserialize JSON
)


        logger.info("Kafka Consumer is Listening......")

        def insert_into_bigquery(data):
            try:
                errors = client.insert_rows_json(table_id, [data])
                if errors:
                    logger.error(f"BigQuery insertion errors: {errors}")
                else:
                    logger.info("Data successfully inserted into BigQuery")
            except Exception as e:
                logger.error(f"BigQuery insertion failed: {e}")

        # Consume messages
        for message in consumer:
            logger.info(f"Received message: {message.value}")
            insert_into_bigquery(message.value)

    except Exception as e:
        logger.error(f"Kafka consumer error: {e}")
        # Implement retry logic if needed


def get_db_connection():
    # initialize Connector object
    connector = Connector()

    # function to return the database connection object
    def getconn():
        conn = connector.connect(
            # Replace with your GCP project, region, and instance details
            instance_connection_string="",    ## instance connection name 
            driver="pymysql",
            user="",   # username 
            password="", # password for the user
            db=""  # database name (instance)
        )
        return conn

    # create SQLAlchemy connection pool
    pool = sqlalchemy.create_engine(
        "mysql+pymysql://",
        creator=getconn,
        # Configure connection pool settings
        pool_size=5,
        max_overflow=2,
        pool_timeout=30,  # 30 seconds
        pool_recycle=1800,  # 30 minutes
    )
    return pool

# Example route to test database connection
@app.route('/test-db')
def test_database():
    try:
        # Get a database connection
        engine = get_db_connection()
        
        with engine.connect() as conn:
            # Prepare the query
            query = text("SELECT Name, UserID, EmailID, Password, Preference FROM usertable")
            
            # Execute the query
            result = conn.execute(query)
            
            # Fetch all rows
            rows = result.fetchall()
            
            # Convert results to a list of dictionaries
            users = []
            for row in rows:
                # Use integer indexing or convert to dict
                try:
                    user = {
                        "Name": row[0],  # Use integer indexing
                        "UserID": row[1],
                        "EmailID": row[2],
                        "Password": row[3],
                        "Preference": row[4]
                    }
                    users.append(user)
                except Exception as row_error:
                    app.logger.error(f"Error processing row: {row_error}")
                    app.logger.error(f"Problematic row: {row}")
            
            return jsonify({
                "status": "success", 
                "count": len(users),
                "users": users,
                "raw_rows": [list(r) for r in rows]  # Add raw row data for debugging
            })
    
    except Exception as e:
        app.logger.error(f"Full database error: {e}")
        return jsonify({
            "status": "error", 
            "message": "Failed to retrieve users",
            "details": str(e)
        }), 500
    

# Before the route, add this to verify connection
@app.route('/db-config')
def show_db_config():
    try:
        # Print out connection details for verification
        print("Attempting to get database connection...")
        engine = get_db_connection()
        
        with engine.connect() as conn:
            # Try a simple query
            result = conn.execute(text("SELECT 1"))
            print("Connection successful!")
            return jsonify({
                "status": "success",
                "message": result
            })
    except Exception as e:
        print(f"Connection error: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


def get_news(api_key, query, language="en", page_size=20, page=1):
    """Fetch news from NewsAPI"""
    url = "https://newsapi.org/v2/everything"
    params = {
        "apiKey": api_key,
        "language": language,
        "pageSize": page_size,
        'page': page,
        "q": query
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching news: {response.status_code}, {response.text}")
        return None

@app.route('/get_news', methods=['GET'])
def get_news_route():
    """Route to fetch news"""
    if 'user_id' not in session:
        session['user_id'] = ''
    
    api_key = os.environ.get('NEWS_API_KEY', '')
    query = request.args.get("query", default='everything')
    page = request.args.get("page", default=10, type=int)

    news_data = get_news(api_key, query=query, page_size=20, page=page)
    if news_data:
        return jsonify({'news_data': news_data, 'userId': session['user_id']})
    else:
        return jsonify({"error": "Failed to fetch news"}), 500

@app.route('/signup', methods=['POST'])
def signup_data():
    """User signup route"""
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')
    preference = data.get('preference')
    userID = name[:2].upper() + str(random.randint(100000, 999999))

    if not all([name, email, password, preference]):
        return jsonify({'error': 'All fields are required'}), 400

    hashed_password = generate_password_hash(password)


    try:
        # Get a database session
        engine = get_db_connection()

        with engine.connect() as conn:
            # Check if email already exists
            email_check = conn.execute(
                text("SELECT COUNT(*) as count FROM usertable WHERE emailID = :email"),
                {'email': email}
            ).scalar()
            
            if email_check > 0:
                return jsonify({'error': 'Email already registered'}), 409

            # Prepare and execute insert query
            insert_query = """
            INSERT INTO usertable (Name, UserID, EmailID, Password, Preference)
            VALUES (:name, :userID, :email, :password, :preference)
            """
            
            conn.execute(
                text(insert_query), 
                {
                    'name': name, 
                    'userID': userID, 
                    'email': email, 
                    'password': hashed_password, 
                    'preference': preference
                }
            )
            
            # Commit the transaction
            conn.commit()
        session['user_id'] = userID

        # Return successful response
        return jsonify({
            'message': 'Signup successful', 
            'userID': userID
        }), 201
    
    except Exception as err:
        app.logger.error(f"Signup error: {err}")
        return jsonify({
            'error': 'Registration failed',
            'details': str(err)
        }), 500
    
    
@app.route('/login', methods=['POST'])
def login():
    """User login route"""
    data = request.get_json()
    email = data.get('email')
    password = data.get('password') 

    if not email or not password:
        return jsonify({'error': 'Email and password are required'}), 400

    try:
        # Get a database session
        engine = get_db_connection()
        
        with engine.connect() as conn:
            # Prepare query to fetch user by email
            query = text("SELECT Name, UserID, Password FROM usertable WHERE EmailID = :email")
            
            # Execute query
            result = conn.execute(query, {'email': email})
            
            # Fetch all rows (should be only one in this case)
            rows = result.fetchall()
            
            # Check if any user found
            if not rows:
                return jsonify({'error': 'Invalid email or password'}), 401
            
            # Parse the first row using integer indexing
            user_data = {
                'Name': rows[0][0],
                'UserID': rows[0][1],
                'Password': rows[0][2]
            }
            
            # Verify password
            if not check_password_hash(user_data['Password'], password):
                return jsonify({'error': 'Invalid email or password'}), 401

            session['user_id'] = user_data['UserID']

            # Return successful login response
            return jsonify({
                'message': 'Login successful', 
                'email': email, 
                'name': user_data['Name'], 
                'userID': user_data['UserID']
            }), 200
    
    except Exception as err:
        app.logger.error(f"Login error: {err}")
        return jsonify({
            'error': 'Login failed',
            'details': str(err)
        }), 500
    
@app.route('/logout', methods=['POST'])
def logout():
    """User logout route"""
    session['user_id'] = ''
    return jsonify({"message": "Logged out successfully", 'user_id': ''}), 200

@app.route('/send_data', methods=['POST'])
def send_data_route():
    """Send data to Kafka"""
    if 'user_id' not in session:
        session['user_id'] = ''
    
    user_id = session['user_id']
    data = request.get_json()
    
    title = data.get("title", "No title provided")
    url = data.get("url", "No URL provided")
    description = data.get("description", "No description provided")
    genre = data.get('query', "General")

    try:
        producer.send('news_data', {
            'UserID': user_id,
            'Title': title,
            'URL': url,
            'Description': description,
            "Genre": genre
        })
        producer.flush()
        return jsonify({
            "status": "success", 
            "user_id": user_id, 
            "title": title, 
            "url": url, 
            "description": description
        })
    except Exception as e:
        print(f"Failed to send data to Kafka: {e}")
        return jsonify({"error": "Failed to send data to Kafka"}), 500

@app.route('/fetch_user_data', methods=['POST'])
def get_user_data():
    """Fetch user data from BigQuery"""
    try:
        # Ensure that session contains 'user_id'
        user_id = session['user_id']
        if not user_id:
            return jsonify({"error": "User ID not found in session"}), 400

        # Initialize BigQuery client
        client = bigquery.Client(credentials=service_account.Credentials.from_service_account_file('credentials_temp.json'))

        # Specify the BigQuery table
        table_id = ""  # big query tableid 
        
        # Query to fetch data for the specific user
        query = f'SELECT * FROM `{table_id}` WHERE userID = @user_id'
        
        query_job = client.query(
            query, 
            job_config=bigquery.QueryJobConfig(
                query_parameters=[
                    bigquery.ScalarQueryParameter('user_id', 'STRING', user_id)
                ]
            )
        )
        
        # Collect the rows from the query result
        rows = list(query_job)

        # If no rows found, return an empty result
        if not rows:
            return jsonify({"message": "No data found for this user"}), 404

        # Return the data as JSON
        return jsonify({
            "message": "Data fetched successfully", 
            "data": [dict(row) for row in rows]
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    consumer_thread = threading.Thread(target=start_kafka_consumer)
    consumer_thread.daemon = True
    consumer_thread.start()

    app.run(host='0.0.0.0', port=8080, debug=True)