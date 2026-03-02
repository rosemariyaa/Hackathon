from flask import Flask, render_template, request, redirect, session, url_for
from flask_mysqldb import MySQL
import config
import os
from werkzeug.utils import secure_filename

# ---------------- Flask App ----------------
app = Flask(__name__)
app.secret_key = "event_secret_key"   # REQUIRED for sessions

# ---------------- Upload configuration ----------------
UPLOAD_FOLDER = "static/images"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# ---------------- MySQL configuration ----------------
app.config['MYSQL_HOST'] = config.MYSQL_HOST
app.config['MYSQL_USER'] = config.MYSQL_USER
app.config['MYSQL_PASSWORD'] = config.MYSQL_PASSWORD
app.config['MYSQL_DB'] = config.MYSQL_DB

mysql = MySQL(app)

# ---------------- Home ----------------
@app.route("/")
def home():
    return render_template("index.html")
# ---------------- About Page ----------------
@app.route("/about")
def about():
    """
    Renders the About Us page with static content.
    """
    return render_template("about.html")


# ---------------- Contact Page ----------------
@app.route("/contact")
def contact():
    """
    Renders the Contact Us page with static contact details.
    """
    return render_template("contact.html")

# ---------------- Login ----------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form['email']
        password = request.form['password']

        cur = mysql.connection.cursor()
        cur.execute(
            "SELECT id, name FROM users WHERE email=%s AND password=%s",
            (email, password)
        )
        user = cur.fetchone()
        cur.close()

        if user:
            session['user_id'] = user[0]
            session['user_name'] = user[1]

            # redirect back if user was sent to login
            return redirect(session.pop("next", "/auditoriums"))

        return render_template("login.html", error="Invalid email or password")

    return render_template("login.html")

# ---------------- Register ----------------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        confirm = request.form['confirm']

        if password != confirm:
            return render_template("register.html", error="Passwords do not match")

        cur = mysql.connection.cursor()
        cur.execute(
            "INSERT INTO users (name, email, password) VALUES (%s,%s,%s)",
            (name, email, password)
        )
        mysql.connection.commit()
        cur.close()

        return redirect("/login")

    return render_template("register.html")

# ---------------- Logout ----------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# ---------------- Auditoriums ----------------
@app.route("/auditoriums")
def auditoriums():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM auditoriums")
    data = cur.fetchall()
    cur.close()
    return render_template("auditoriums.html", data=data)

# ---------------- Add Auditorium ----------------
@app.route("/add-auditorium", methods=["GET", "POST"])
def add_auditorium():
    if request.method == "POST":
        name = request.form['name']
        location = request.form['location']
        phone = request.form['phone']
        price = request.form['price']
        image = request.files['image']

        filename = secure_filename(image.filename)
        image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        cur = mysql.connection.cursor()
        cur.execute(
            """INSERT INTO auditoriums
               (name, location, phone, price, image)
               VALUES (%s,%s,%s,%s,%s)""",
            (name, location, phone, price, filename)
        )
        mysql.connection.commit()
        cur.close()

        return redirect("/auditoriums")

    return render_template("add_auditorium.html")
@app.route("/book/<int:aid>")
def book(aid):

    # user must be logged in
    if "user_id" not in session:
        session["next"] = url_for("book", aid=aid)
        return redirect("/login")

    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM auditoriums WHERE id=%s", (aid,))
    auditorium = cur.fetchone()
    cur.close()

    return render_template("book.html", auditorium=auditorium)
# ---------------- Add Decoration (Admin) ----------------
@app.route("/add-decoration", methods=["GET", "POST"])
def add_decoration():
    # Optional: check if admin logged in
    # if 'user_id' not in session:
    #     return redirect('/login')

    if request.method == "POST":
        name = request.form["name"]
        price = request.form["price"]
        image = request.files["image"]

        filename = secure_filename(image.filename)
        image.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))

        cur = mysql.connection.cursor()
        cur.execute(
            "INSERT INTO decoration (name, price, image) VALUES (%s, %s, %s)",
            (name, price, filename)
        )
        mysql.connection.commit()
        cur.close()

        return redirect("/decoration")

    return render_template("add_decoration.html")


# ---------------- Display Decorations ----------------
@app.route("/decoration")
def decorations():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM decoration")
    data = cur.fetchall()
    cur.close()
    return render_template("decoration.html", data=data)

# ---------------- Run App ----------------
if __name__ == "__main__":
    app.run(debug=True) 