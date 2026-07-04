from flask import Flask, request, jsonify
from flask_cors import CORS
import pickle
import sqlite3

app = Flask(__name__)
CORS(app)

# Load model
model = pickle.load(open("model.pkl", "rb"))

# ---------------- DATABASE ---------------- #

def init_db():
    conn = sqlite3.connect("hospital.db")
    cursor = conn.cursor()

    # Users table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        password TEXT,
        role TEXT
    )
    """)

    # Patients table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS patients (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        age INTEGER,
        bp INTEGER,
        sugar INTEGER,
        cholesterol INTEGER,
        risk INTEGER,
        score INTEGER,
        status TEXT,
        recommendation TEXT
    )
    """)

    # Settings table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS settings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        doctor TEXT,
        email TEXT,
        phone TEXT,
        hospital TEXT,
        location TEXT,
        department TEXT
    )
    """)

    conn.commit()
    conn.close()


def create_admin():
    conn = sqlite3.connect("hospital.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE username=?", ("admin",))
    if not cursor.fetchone():
        cursor.execute(
            "INSERT INTO users (username,password,role) VALUES (?,?,?)",
            ("admin", "1234", "admin")
        )

    conn.commit()
    conn.close()


# Run DB setup
init_db()
create_admin()

# ---------------- ROUTES ---------------- #

@app.route('/')
def home():
    return "AI Healthcare Backend Running"


@app.route('/predict', methods=['POST'])
def predict():

    data = request.json

    age = int(data['age'])
    bp = int(data['bp'])
    sugar = int(data['sugar'])
    cholesterol = int(data['cholesterol'])

    prediction = model.predict([[age, bp, sugar, cholesterol]])
    risk = int(prediction[0])

    score = 100 - (0.1*bp + 0.1*sugar + 0.05*cholesterol)
    score = max(0, min(100, int(score)))

    if score >= 80:
        status = "Very Healthy"
    elif score >= 60:
        status = "Moderate"
    elif score >= 40:
        status = "Risk"
    else:
        status = "High Risk"

    if status == "Very Healthy":
        recommendation = "Maintain your lifestyle."
    elif status == "Moderate":
        recommendation = "Maintain balanced diet."
    elif status == "Risk":
        recommendation = "Exercise regularly."
    else:
        recommendation = "Consult doctor."

    # Save to DB
    conn = sqlite3.connect("hospital.db")
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO patients (age, bp, sugar, cholesterol, risk, score, status, recommendation)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (age, bp, sugar, cholesterol, risk, score, status, recommendation))

    conn.commit()
    conn.close()

    return jsonify({
        "risk": risk,
        "score": score,
        "status": status,
        "recommendation": recommendation
    })


@app.route('/patients', methods=['GET'])
def get_patients():
    conn = sqlite3.connect("hospital.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM patients")
    data = cursor.fetchall()

    conn.close()
    return jsonify(data)


@app.route('/delete/<int:id>', methods=['DELETE'])
def delete_patient(id):
    conn = sqlite3.connect("hospital.db")
    cursor = conn.cursor()

    cursor.execute("DELETE FROM patients WHERE id=?", (id,))
    conn.commit()
    conn.close()

    return jsonify({"message": "Deleted"})


@app.route('/update/<int:id>', methods=['PUT'])
def update_patient(id):

    data = request.json

    conn = sqlite3.connect("hospital.db")
    cursor = conn.cursor()

    cursor.execute("""
    UPDATE patients
    SET age=?, bp=?, sugar=?, cholesterol=?
    WHERE id=?
    """, (data['age'], data['bp'], data['sugar'], data['cholesterol'], id))

    conn.commit()
    conn.close()

    return jsonify({"message": "Updated"})


# ✅ FIXED LOGIN
@app.route('/login', methods=['POST'])
def login():
    data = request.json

    conn = sqlite3.connect("hospital.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM users WHERE username=? AND password=?",
        (data['username'], data['password'])
    )

    user = cursor.fetchone()
    conn.close()

    if user:
        return jsonify({"status": "success", "role": user[3]})
    else:
        return jsonify({"status": "fail"})


@app.route('/save_settings', methods=['POST'])
def save_settings():
    data = request.json

    conn = sqlite3.connect("hospital.db")
    cursor = conn.cursor()

    cursor.execute("DELETE FROM settings")

    cursor.execute("""
    INSERT INTO settings (doctor,email,phone,hospital,location,department)
    VALUES (?,?,?,?,?,?)
    """, (data['doctor'], data['email'], data['phone'],
          data['hospital'], data['location'], data['department']))

    conn.commit()
    conn.close()

    return jsonify({"msg": "saved"})


if __name__ == '__main__':
    app.run(debug=True)