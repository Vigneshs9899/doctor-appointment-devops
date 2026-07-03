from flask import (
    Flask,
    jsonify,
    request,
    render_template,
    redirect,
    session,
    flash
)

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle
)

from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet
from datetime import datetime

from pendulum import today
from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

import time
import psycopg2
import os
from flask import send_file

app = Flask(__name__)
app.secret_key = "mysecretkey"

@app.route("/")
def home():
    return render_template("home.html")


@app.route("/dashboard")
def dashboard():

    if "user" not in session:
        return redirect("/login")

    return render_template("index.html")

# Wait for DB connection
while True:
    try:
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            database=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            port=os.getenv("DB_PORT", "5432")
        )

        cursor = conn.cursor()

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS appointments (
            id SERIAL PRIMARY KEY,
            name TEXT,
            doctor TEXT
        )
        """)

        cursor.execute("""
        ALTER TABLE appointments
        ADD COLUMN IF NOT EXISTS appointment_time TIMESTAMP
        """)

        conn.commit()

        cursor.execute("""
        ALTER TABLE appointments
        ADD COLUMN IF NOT EXISTS user_id INTEGER
        """)

        conn.commit()

        cursor.execute("""
        ALTER TABLE appointments
        ADD COLUMN IF NOT EXISTS status TEXT
        DEFAULT 'Pending'
        """)

        conn.commit()

        cursor.execute("""
        ALTER TABLE appointments
        ADD COLUMN IF NOT EXISTS symptoms TEXT
        """)
        conn.commit()
        
        cursor.execute("""
        ALTER TABLE appointments
        ADD COLUMN IF NOT EXISTS prescription TEXT
        """)
        conn.commit()
        
        cursor.execute("""
        ALTER TABLE appointments
        ADD COLUMN IF NOT EXISTS doctor_notes TEXT
        """)
        conn.commit()
        
        cursor.execute("""
        ALTER TABLE appointments
        ADD COLUMN IF NOT EXISTS followup_date DATE
        """)
        conn.commit()

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        username TEXT UNIQUE,
        password TEXT
        )
        """)

        conn.commit()

        cursor.execute("""
        ALTER TABLE users
        ADD COLUMN IF NOT EXISTS role TEXT DEFAULT 'patient'
        """)

        conn.commit()

        print("Database connected ✅")
        break

    except Exception as e:
        print("Waiting for DB...", e)
        time.sleep(2)
# POST
@app.route('/appointments', methods=['POST'])

def add_appointment():

    if 'user' not in session:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json()

    cursor.execute(
    """
    INSERT INTO appointments
(
    name,
    doctor,
    appointment_time,
    user_id,
    symptoms
)
VALUES
(
    %s,%s,%s,%s,%s
)
    """,
    (
   data["name"],
    data["doctor"],
    data["appointment_time"],
    session["user_id"],
    data["symptoms"]
    )
)

    conn.commit()

    return jsonify({"message": "Appointment added"})


#delete
@app.route('/appointments/<int:id>', methods=['DELETE'])
def delete_appointment(id):

    if 'user' not in session:
        return jsonify({"error": "Unauthorized"}), 401

    cursor.execute(
        "DELETE FROM appointments WHERE id = %s",
        (id,)
    )

    conn.commit()

    return jsonify({"message": "Deleted"})



# GET
@app.route('/appointments', methods=['GET'])
def get_appointments():

    if 'user' not in session:
        return jsonify([]), 401

    search = request.args.get('search', '')

    cursor.execute(
    """
    SELECT * FROM appointments
    WHERE user_id = %s
    AND doctor ILIKE %s
    ORDER BY appointment_time
    """,
    (
        session['user_id'],
        f'%{search}%'
    )
    )
    rows = cursor.fetchall()

    result = []

    for row in rows:
        result.append({
            "id": row[0],
            "name": row[1],
            "doctor": row[2],
            "appointment_time": row[3],
            "user_id": row[4],
            "status": row[5],
            "symptoms": row[7]
        })

    return jsonify(result)

#update
@app.route('/appointments/<int:id>', methods=['PUT'])
def update_appointment(id):

    if 'user' not in session:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json()

    cursor.execute(
        """
        UPDATE appointments
        SET name=%s,
            doctor=%s,
            appointment_time=%s
        WHERE id=%s
        """,
        (
            data['name'],
            data['doctor'],
            data['appointment_time'],
            id
        )
    )

    conn.commit()

    return jsonify({
        "message": "Appointment updated"
    })

#signup
@app.route('/signup', methods=['GET', 'POST'])
def signup():

    if request.method == 'POST':

        username = request.form['username']

        password = generate_password_hash(
            request.form['password']
        )

        cursor.execute(
            """
            INSERT INTO users
            (username,password,role)
            VALUES (%s,%s,'patient')
            """,
            (username, password)
        )

        conn.commit()

        flash("Account created successfully!")

        return redirect('/login')

    return render_template('signup.html')

#login
@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']

        cursor.execute(
            """
            SELECT * FROM users
            WHERE username = %s
            """,
            (username,)
        )

        user = cursor.fetchone()

        if user and check_password_hash(
            user[2],
            password
    ):

            session["user"] = username
            session["user_id"] = user[0]
            session["role"] = user[3]

            if user[3] == "doctor":
                return redirect("/doctor")

            return redirect("/dashboard")

        flash("Invalid username or password")

        return redirect('/login')

    return render_template('login.html')

#logout
@app.route('/logout')
def logout():

    session.pop('user', None)

    return redirect('/')

@app.route("/doctor")
def doctor_dashboard():

    if "user" not in session:
        return redirect("/login")

    if session.get("role") != "doctor":
        return redirect("/dashboard")

    cursor.execute("SELECT COUNT(*) FROM appointments")
    total = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*)
        FROM appointments
        WHERE status='Pending'
    """)
    pending = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*)
        FROM appointments
        WHERE status='Completed'
    """)
    completed = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*)
        FROM appointments
        WHERE DATE(appointment_time)=CURRENT_DATE
    """)
    today = cursor.fetchone()[0]


    cursor.execute("""
    SELECT
        id,
        name,
        doctor,
        appointment_time,
        status
    FROM appointments
    ORDER BY appointment_time DESC
    """)

    appointments = cursor.fetchall()

    # Status Chart
    cursor.execute("""
    SELECT status, COUNT(*)
    FROM appointments
    GROUP BY status
    """)
    status_chart = cursor.fetchall()
    
    # Monthly Chart
    cursor.execute("""
    SELECT
    TO_CHAR(appointment_time,'Mon') AS month,
    COUNT(*)
    FROM appointments
    GROUP BY month
    ORDER BY MIN(appointment_time)
    """)
    monthly_chart = cursor.fetchall()



    return render_template(
    "doctor_dashboard.html",
    total=total,
    pending=pending,
    completed=completed,
    today=today,
    appointments=appointments,
    status_chart=status_chart,
    monthly_chart=monthly_chart
    )

#status change
@app.route('/appointments/<int:id>/status',
methods=['PUT'])

def update_status(id):

    if 'user' not in session:
        return jsonify({
            "error": "Unauthorized"
        }), 401

    data = request.get_json()

    cursor.execute(
        """
        UPDATE appointments
        SET status=%s
        WHERE id=%s
        """,
        (
            data['status'],
            id
        )
    )

    conn.commit()

    return jsonify({
        "message": "Status updated"
    })

@app.route("/consultation/<int:id>")
def consultation(id):

    if "user" not in session:
        return redirect("/login")

    if session.get("role") != "doctor":
        return redirect("/dashboard")

    cursor.execute("""
    SELECT *
    FROM appointments
    WHERE id=%s
    """, (id,))

    appointment = cursor.fetchone()

    return render_template(
        "consultation.html",
        appointment=appointment
    )


@app.route("/consultation/<int:id>", methods=["POST"])
def save_consultation(id):

    if "user" not in session:
        return redirect("/login")

    if session.get("role") != "doctor":
        return redirect("/dashboard")

    diagnosis = request.form["diagnosis"]
    prescription = request.form["prescription"]
    doctor_notes = request.form["doctor_notes"]
    followup_date = request.form["followup_date"]
    status = request.form["status"]

    cursor.execute("""
    UPDATE appointments
    SET
        diagnosis=%s,
        prescription=%s,
        doctor_notes=%s,
        followup_date=%s,
        status=%s
    WHERE id=%s
    """,
    (
        diagnosis,
        prescription,
        doctor_notes,
        followup_date,
        status,
        id
    ))

    conn.commit()

    flash("Consultation saved successfully!")

    return redirect("/doctor")


@app.route("/report/<int:id>")
def patient_report(id):

    if "user" not in session:
        return redirect("/login")

    cursor.execute("""
        SELECT *
        FROM appointments
        WHERE id=%s
        AND user_id=%s
    """,
    (
        id,
        session["user_id"]
    ))

    appointment = cursor.fetchone()

    if not appointment:
        return "Appointment not found",404

    return render_template(
        "patient_report.html",
        appointment=appointment
    )

@app.route("/report/<int:id>/pdf")
def download_pdf(id):

    if "user" not in session:
        return redirect("/login")

    cursor.execute("""
        SELECT *
        FROM appointments
        WHERE id=%s
        AND user_id=%s
    """, (id, session["user_id"]))

    appointment = cursor.fetchone()

    if not appointment:
        return "Appointment not found", 404

    filename = f"Medical_Report_{appointment[1]}_{appointment[0]}.pdf"

    styles = getSampleStyleSheet()

    title = styles["Title"]
    title.alignment = 1
    title.textColor = colors.darkgreen

    heading = styles["Heading2"]
    heading.textColor = colors.darkgreen

    body = styles["BodyText"]

    generated_time = datetime.now().strftime("%d %b %Y %I:%M %p")

    doc = SimpleDocTemplate(
        filename,
        leftMargin=40,
        rightMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    story = []

    # -------------------------------------------------
    # Header
    # -------------------------------------------------

    story.append(
        Paragraph(
            "<font size='24'><b>🌿 SHAYURE AYURVEDA</b></font>",
            title
        )
    )

    story.append(
        Paragraph(
            "<font size='15'>Medical Consultation Report</font>",
            title
        )
    )

    story.append(Spacer(1, 20))

    story.append(
        Paragraph(
            f"<b>Report ID:</b> #{appointment[0]}",
            body
        )
    )

    story.append(
        Paragraph(
            f"<b>Generated On:</b> {generated_time}",
            body
        )
    )

    story.append(Spacer(1, 20))

    # -------------------------------------------------
    # Patient Information
    # -------------------------------------------------

    story.append(
        Paragraph("<b>Patient Information</b>", heading)
    )

    story.append(Spacer(1, 10))

    patient_data = [

        ["Patient Name", appointment[1]],

        ["Doctor", appointment[2]],

        ["Appointment Time", str(appointment[3])],

        ["Status", appointment[5]]

    ]

    patient_table = Table(
        patient_data,
        colWidths=[170, 310]
    )

    patient_table.setStyle(TableStyle([

        ("GRID", (0,0), (-1,-1), 0.5, colors.grey),

        ("BACKGROUND", (0,0), (0,-1), colors.HexColor("#C8E6C9")),

        ("FONTNAME", (0,0), (-1,-1), "Helvetica"),

        ("FONTSIZE", (0,0), (-1,-1), 11),

        ("BOTTOMPADDING", (0,0), (-1,-1), 8),

        ("TOPPADDING", (0,0), (-1,-1), 8),

        ("VALIGN",(0,0),(-1,-1),"MIDDLE")

    ]))

    story.append(patient_table)

    story.append(Spacer(1, 25))

    # -------------------------------------------------
    # Medical Details
    # -------------------------------------------------

    story.append(
        Paragraph("<b>Medical Details</b>", heading)
    )

    story.append(Spacer(1, 10))

    medical_data = [

        ["Symptoms", appointment[7] or "-"],

        ["Diagnosis", appointment[10] or "-"],

        ["Prescription", appointment[8] or "-"],

        ["Doctor Notes", appointment[9] or "-"],

        ["Follow-up Date", str(appointment[6] or "-")]

    ]

    medical_table = Table(
        medical_data,
        colWidths=[170, 310]
    )

    medical_table.setStyle(TableStyle([

        ("GRID", (0,0), (-1,-1), 0.5, colors.grey),

        ("BACKGROUND", (0,0), (0,-1), colors.HexColor("#FFF3CD")),

        ("FONTNAME", (0,0), (-1,-1), "Helvetica"),

        ("FONTSIZE", (0,0), (-1,-1), 11),

        ("BOTTOMPADDING", (0,0), (-1,-1), 10),

        ("TOPPADDING", (0,0), (-1,-1), 10),

        ("VALIGN",(0,0),(-1,-1),"TOP")

    ]))

    story.append(medical_table)

    story.append(Spacer(1, 35))

    # -------------------------------------------------
    # Signature
    # -------------------------------------------------

    story.append(
        Paragraph(
            "________________________________________",
            body
        )
    )

    story.append(
        Paragraph(
            "<b>Doctor Signature</b>",
            body
        )
    )

    story.append(Spacer(1, 25))

    # -------------------------------------------------
    # Footer
    # -------------------------------------------------

    story.append(
        Paragraph(
            "<font color='grey'>Generated by SHAYURE AYURVEDA Doctor Appointment System</font>",
            body
        )
    )

    story.append(
        Paragraph(
            "<font color='grey'>Thank you for choosing SHAYURE AYURVEDA.</font>",
            body
        )
    )

    story.append(
        Paragraph(
            "<font color='grey'>Get Well Soon 🌿</font>",
            body
        )
    )

    doc.build(story)

    return send_file(
        filename,
        as_attachment=True
    )

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(
        host="0.0.0.0",
        port=port,
        debug=True
    )
