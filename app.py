import time
import os
import psycopg2
from flask import Flask, jsonify, request

# Wait for DB
while True:
    try:
        conn = psycopg2.connect(
        host="db",
        database=os.getenv("POSTGRES_DB"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD")
    )
        break
    except:
        print("Waiting for database...")
        time.sleep(2)

cursor = conn.cursor()

# Create table
cursor.execute("""
CREATE TABLE IF NOT EXISTS appointments (
    id SERIAL PRIMARY KEY,
    name TEXT,
    doctor TEXT
)
""")
conn.commit()

app = Flask(__name__)

# POST
@app.route('/appointments', methods=['POST'])
def add_appointment():
    data = request.get_json()

    if not data:
        return jsonify({"error": "No data"}), 400

    cursor.execute(
        "INSERT INTO appointments (name, doctor) VALUES (%s, %s) RETURNING id",
        (data['name'], data['doctor'])
    )
    new_id = cursor.fetchone()[0]
    conn.commit()

    return jsonify({"id": new_id, "message": "added"}), 201


# GET
@app.route('/appointments', methods=['GET'])
def get_appointments():
    cursor.execute("SELECT * FROM appointments")
    rows = cursor.fetchall()

    result = []
    for row in rows:
        result.append({
            "id": row[0],
            "name": row[1],
            "doctor": row[2]
        })

    return jsonify(result)


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)