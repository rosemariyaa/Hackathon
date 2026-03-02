from flask import Flask, render_template, request, redirect, session, url_for
from flask_mysqldb import MySQL
import config
import os
from werkzeug.utils import secure_filename

# ---------------- Flask App ----------------
app = Flask(__name__)
app.secret_key = "event_secret_key"

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

# ---------------- Home / About / Contact ----------------
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/contact")
def contact():
    return render_template("contact.html")

# ---------------- Login ----------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form['email']
        password = request.form['password']

        cur = mysql.connection.cursor()
        cur.execute("SELECT id, name FROM users WHERE email=%s AND password=%s", (email, password))
        user = cur.fetchone()
        cur.close()

        if user:
            session['user_id'] = user[0]
            session['user_name'] = user[1]

            # Admin check
            if email == "rosemariya2910@gmail.com" and password == "171329@Ar":
                session["user_role"] = "admin"
                return redirect("/admin")

            # Normal user
            session["user_role"] = "user"
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
        cur.execute("INSERT INTO users (name, email, password) VALUES (%s,%s,%s)", (name, email, password))
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

# ---------------- Add Auditorium (User) ----------------
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
            "INSERT INTO auditoriums (name, location, phone, price, image) VALUES (%s,%s,%s,%s,%s)",
            (name, location, phone, price, filename)
        )
        mysql.connection.commit()
        cur.close()
        return redirect("/auditoriums")
    return render_template("add_auditorium.html")

# ---------------- Admin Dashboard ----------------
@app.route("/admin")
def admin_dashboard():
    if "user_role" not in session or session["user_role"] != "admin":
        return redirect("/login")
    return render_template("admin_dashboard.html", user_name=session.get("user_name"))

# ---------------- Admin Users ----------------
@app.route("/admin/users")
def admin_users():
    if "user_role" not in session or session["user_role"] != "admin":
        return redirect("/login")

    cur = mysql.connection.cursor()
    cur.execute("SELECT id, name, email FROM users")
    users = cur.fetchall()
    cur.close()
    return render_template("admin_users.html", users=users)

@app.route("/admin/users/edit/<int:uid>", methods=["GET", "POST"])
def edit_user(uid):
    if "user_role" not in session or session["user_role"] != "admin":
        return redirect("/login")
    cur = mysql.connection.cursor()
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        cur.execute("UPDATE users SET name=%s, email=%s WHERE id=%s", (name, email, uid))
        mysql.connection.commit()
        cur.close()
        return redirect(url_for("admin_users"))
    cur.execute("SELECT id, name, email FROM users WHERE id=%s", (uid,))
    user = cur.fetchone()
    cur.close()
    return render_template("edit_user.html", user=user)

@app.route("/admin/users/delete/<int:uid>", methods=["GET", "POST"])
def delete_user(uid):
    if "user_role" not in session or session["user_role"] != "admin":
        return redirect("/login")
    cur = mysql.connection.cursor()
    if request.method == "GET":
        cur.execute("SELECT id, name, email FROM users WHERE id=%s", (uid,))
        user = cur.fetchone()
        cur.close()
        return render_template("delete.html", user=user)
    cur.execute("DELETE FROM users WHERE id=%s", (uid,))
    mysql.connection.commit()
    cur.close()
    return redirect(url_for("admin_users"))

# ---------------- Admin Auditoriums ----------------
@app.route("/admin/auditoriums")
def admin_auditoriums():
    if "user_role" not in session or session["user_role"] != "admin":
        return redirect("/login")
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM auditoriums")
    auditoriums = cur.fetchall()
    cur.close()
    return render_template("admin_auditoriums.html", auditoriums=auditoriums)

@app.route("/admin/auditoriums/add", methods=["GET", "POST"])
def add_auditorium_admin():
    if "user_role" not in session or session["user_role"] != "admin":
        return redirect("/login")
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
            "INSERT INTO auditoriums (name, location, phone, price, image) VALUES (%s,%s,%s,%s,%s)",
            (name, location, phone, price, filename)
        )
        mysql.connection.commit()
        cur.close()
        return redirect(url_for("admin_auditoriums"))
    return render_template("add_auditorium.html")

@app.route("/admin/edit-auditorium/<int:aid>", methods=["GET", "POST"])
def edit_auditorium(aid):
    if "user_role" not in session or session["user_role"] != "admin":
        return redirect("/login")
    cur = mysql.connection.cursor()
    if request.method == "POST":
        name = request.form['name']
        location = request.form['location']
        phone = request.form['phone']
        price = request.form['price']
        image = request.files.get('image')
        if image and image.filename != '':
            filename = secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            cur.execute(
                "UPDATE auditoriums SET name=%s, location=%s, phone=%s, price=%s, image=%s WHERE id=%s",
                (name, location, phone, price, filename, aid)
            )
        else:
            cur.execute(
                "UPDATE auditoriums SET name=%s, location=%s, phone=%s, price=%s WHERE id=%s",
                (name, location, phone, price, aid)
            )
        mysql.connection.commit()
        cur.close()
        return redirect(url_for("admin_auditoriums"))
    cur.execute("SELECT * FROM auditoriums WHERE id=%s", (aid,))
    auditorium = cur.fetchone()
    cur.close()
    return render_template("edit_auditorium.html", auditorium=auditorium)

@app.route("/admin/auditoriums/delete/<int:aid>", methods=["GET", "POST"])
def delete_auditorium_admin(aid):
    if "user_role" not in session or session["user_role"] != "admin":
        return redirect("/login")
    cur = mysql.connection.cursor()
    if request.method == "GET":
        cur.execute("SELECT * FROM auditoriums WHERE id=%s", (aid,))
        auditorium = cur.fetchone()
        cur.close()
        return render_template("delete_auditorium.html", auditorium=auditorium)
    cur.execute("DELETE FROM auditoriums WHERE id=%s", (aid,))
    mysql.connection.commit()
    cur.close()
    return redirect(url_for("admin_auditoriums"))

# ---------------- Admin Decorations ----------------
@app.route("/admin/decorations")
def admin_decorations():
    if "user_role" not in session or session["user_role"] != "admin":
        return redirect("/login")
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM decoration")
    decorations = cur.fetchall()
    cur.close()
    return render_template("admin_decorations.html", decorations=decorations)

# ---------------- Run App ----------------
if __name__ == "__main__":
    app.run(debug=True)