import time
import psycopg2
import os
from flask import Flask, jsonify, request

app = Flask(__name__)

conn = None
cursor = None

# Try DB connection (but don't crash if fails)
try:
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST", "db"),  # default for docker
        database=os.getenv("POSTGRES_DB", "appointments_db"),
        user=os.getenv("POSTGRES_USER", "admin"),
        password=os.getenv("POSTGRES_PASSWORD", "admin123")
    )
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS appointments (
        id SERIAL PRIMARY KEY,
        name TEXT,
        doctor TEXT
    )
    """)
    conn.commit()

    print("Connected to database ✅")

except Exception as e:
    print("Database not available, running without DB ❌")
    print(e)

# fallback memory storage
appointments = []

# POST
@app.route('/appointments', methods=['POST'])
def add_appointment():
    data = request.get_json()

    if not data:
        return jsonify({"error": "No data"}), 400

    # If DB available
    if cursor:
        cursor.execute(
            "INSERT INTO appointments (name, doctor) VALUES (%s, %s) RETURNING id",
            (data['name'], data['doctor'])
        )
        new_id = cursor.fetchone()[0]
        conn.commit()

        return jsonify({"id": new_id, "message": "added"}), 201

    # fallback
    data['id'] = len(appointments) + 1
    appointments.append(data)
    return jsonify(data), 201


# GET
@app.route('/appointments', methods=['GET'])
def get_appointments():
    if cursor:
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

    return jsonify(appointments)


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
