from flask import Flask, render_template, request, redirect
from flask_mysqldb import MySQL
from werkzeug.utils import secure_filename
import os
import config

# ✅ FIRST create Flask app
app = Flask(__name__)

# ✅ THEN configure upload folder
UPLOAD_FOLDER = "static/images"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# ---------------- MySQL configuration ----------------
app.config['MYSQL_HOST'] = config.MYSQL_HOST
app.config['MYSQL_USER'] = config.MYSQL_USER
app.config['MYSQL_PASSWORD'] = config.MYSQL_PASSWORD
app.config['MYSQL_DB'] = config.MYSQL_DB

mysql = MySQL(app)

# ---------------- Home page ----------------
@app.route("/")
def home():
    return render_template("index.html")

# ---------------- Login page ----------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form['email']
        password = request.form['password']
        # validation / authentication later
    return render_template("login.html")

# ---------------- Auditoriums page ----------------
@app.route("/auditoriums")
def auditoriums():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM auditoriums")
    data = cursor.fetchall()
    cursor.close()

    return render_template("auditoriums.html", data=data)

# ---------------- Catering page ----------------
@app.route("/catering")
def catering():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM catering")
    data = cursor.fetchall()
    cursor.close()

    return render_template("catering.html", data=data)

# ---------------- Decoration page ----------------
@app.route("/decoration")
def decoration():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM decoration")
    data = cursor.fetchall()
    cursor.close()

    return render_template("decoration.html", data=data)

# ---------------- Makeup page ----------------
@app.route("/makeup")
def makeup():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM makeup")
    data = cursor.fetchall()
    cursor.close()

    return render_template("makeup.html", data=data)

@app.route("/add-auditorium", methods=["GET", "POST"])
def add_auditorium():
    if request.method == "POST":
        name = request.form['name']
        location = request.form['location']
        phone = request.form['phone']
        price = request.form['price']
        image_file = request.files['image']

        # Secure image filename
        filename = secure_filename(image_file.filename)

        # Save image to static/images
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        image_file.save(image_path)

        cursor = mysql.connection.cursor()
        cursor.execute(
            cursor.execute(
    "INSERT INTO auditoriums (name, location, phone, price, image) VALUES (%s, %s, %s, %s, %s)",
    (name, location, phone, price, filename)
)
            (name, location, price, filename)
        )
        mysql.connection.commit()
        cursor.close()

        return redirect("/auditoriums")

    return render_template("add_auditorium.html")

# ---------------- Add Decoration (Admin) ----------------
@app.route("/add-decoration", methods=["GET", "POST"])
def add_decoration():
    if request.method == "POST":
        name = request.form['name']
        price = request.form['price']
        image_file = request.files['image']

        filename = secure_filename(image_file.filename)
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        image_file.save(image_path)

        cursor = mysql.connection.cursor()
        cursor.execute(
            "INSERT INTO decoration (name, price, image) VALUES (%s, %s, %s)",
            (name, price, filename)
        )
        mysql.connection.commit()
        cursor.close()

        return redirect("/decoration")

    return render_template("add_decoration.html")
# ---------------- Run app ----------------
if __name__ == "__main__":
    app.run(debug=True)