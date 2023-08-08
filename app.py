from flask import Flask, jsonify
import os
import requests
import psycopg2

app = Flask(__name__)

db_url = os.environ.get('DATABASE_URL')
app_port = os.environ.get('PORT')

if db_url is None:
    raise ValueError("DATABASE_URL environment variable not set")
  
# Database connection
conn = psycopg2.connect(db_url)

# Bored API base URL
BORED_API_BASE_URL = 'https://www.boredapi.com/api/'


def get_random_activity():
    """Retrieve a random activity from Bored API"""
    response = requests.get(BORED_API_BASE_URL + 'activity')
    if response.status_code == 200:
        data = response.json()
        return data.get('activity')
    else:
        return None


@app.route('/insert_activity', methods=['GET'])
def insert_activity():
    """Insert a random activity generated from BoredAPI into the Render-created PostgeSQL database table"""
    try:
        with conn:
            with conn.cursor() as cursor:
                activity_name = get_random_activity()
                if get_random_activity():
                    cursor.execute('INSERT INTO my_activities (activity) VALUES (%s)', (activity_name,))
                    conn.commit()
                    return jsonify({'status': 'success', 'message': f'Activity "{activity_name}" inserted successfully'})
                else:
                    return jsonify({'status': 'error', 'message': 'Unable to generate an activity from BoredAPI'}), 400
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/')
def index():
    """Homepage that shows all inserted activity names and the total count"""
    try:
        with conn:
            with conn.cursor() as cursor:
                cursor.execute('SELECT COUNT(*) FROM my_activities')
                count = cursor.fetchone()[0]

                cursor.execute('SELECT activity FROM my_activities')
                activity_names = [row[0] for row in cursor.fetchall()]
                return jsonify({'activity_count': count, 'activities': activity_names})

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, port=app_port)
