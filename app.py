
import os
from flask import Flask, request, redirect, render_template_string
import psycopg2

app = Flask(__name__)

def get_db():
    return psycopg2.connect(
        os.environ["DATABASE_URL"],
        sslmode="require"
    )

def init_db():
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS Patients (
                    patient_id INT PRIMARY KEY,
                    patient_name VARCHAR(100),
                    age INT,
                    disease VARCHAR(100),
                    phone VARCHAR(15)
                )
            """)

@app.route("/", methods=["GET", "POST"])
def home():
    init_db()

    if request.method == "POST":
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO Patients
                    (patient_id, patient_name, age, disease, phone)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (patient_id) DO NOTHING
                """, (
                    request.form["patient_id"],
                    request.form["patient_name"],
                    request.form["age"],
                    request.form["disease"],
                    request.form["phone"]
                ))
        return redirect("/")

    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT patient_id, patient_name, age, disease, phone
                FROM Patients ORDER BY patient_id
            """)
            patients = cur.fetchall()

    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
      <title>Hospital Management</title>
      <style>
        body {font-family:Arial; max-width:900px; margin:40px auto;
              background:#f3f6fa; color:#243247}
        h1 {color:#145a75}
        form, table {background:white; padding:18px; width:100%;
                     box-sizing:border-box; border-radius:8px}
        input {padding:10px; margin:5px; max-width:150px}
        button {padding:10px; background:#145a75; color:white;
                border:0; cursor:pointer}
        table {margin-top:20px; border-collapse:collapse}
        th,td {padding:10px; border-bottom:1px solid #ddd}
      </style>
    </head>
    <body>
      <h1>Hospital Management System</h1>
      <h3>Add Patient</h3>
      <form method="post">
        <input name="patient_id" type="number" placeholder="Patient ID" required>
        <input name="patient_name" placeholder="Patient Name" required>
        <input name="age" type="number" placeholder="Age" required>
        <input name="disease" placeholder="Disease" required>
        <input name="phone" placeholder="Phone" required>
        <button type="submit">Add Patient</button>
      </form>
      <h3>Patient Records</h3>
      <table>
        <tr><th>ID</th><th>Name</th><th>Age</th>
            <th>Disease</th><th>Phone</th></tr>
        {% for p in patients %}
        <tr>{% for value in p %}<td>{{ value }}</td>{% endfor %}</tr>
        {% endfor %}
      </table>
    </body>
    </html>
    """, patients=patients)

@app.route("/update/<int:patient_id>", methods=["POST"])
def update_patient(patient_id):
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE Patients SET disease = %s
                WHERE patient_id = %s
            """, (request.form["disease"], patient_id))
    return redirect("/")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
