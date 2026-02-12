from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)
def init_db():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT UNIQUE,
            password TEXT,
            role TEXT
        )
    ''')

    c.execute('''
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        price INTEGER,
        quantity INTEGER,
        status TEXT
    )
    ''')
    
    c.execute('''
    CREATE TABLE IF NOT EXISTS cart (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_id INTEGER,
        quantity INTEGER
    )
    ''')

    c.execute('''
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_name TEXT,
        price INTEGER,
        quantity INTEGER,
        total INTEGER
    )
    ''')



    conn.commit()
    conn.close()

init_db()  
@app.route("/")
def home():
    return render_template("login.html")

@app.route("/signup")
def signup_page():
    return render_template("signup.html")

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard_user.html")

@app.route("/add_product", methods=["POST"])
def add_product():
    name = request.form["name"]
    price = request.form["price"]
    quantity = request.form["quantity"]
    status = request.form["status"]

    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    c.execute("INSERT INTO products (name,price,quantity,status) VALUES (?,?,?,?)",
              (name, price, quantity, status))

    conn.commit()
    conn.close()

    return render_template("dashboard_vendor.html")

@app.route("/products")
def products():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("SELECT * FROM products")
    products = c.fetchall()
    conn.close()
    return render_template("products.html", products=products)

@app.route("/add_to_cart", methods=["POST"])
def add_to_cart():
    product_id = request.form["product_id"]
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("INSERT INTO cart (product_id, quantity) VALUES (?, ?)",
              (product_id, 1))

    conn.commit()
    conn.close()

    return render_template("cart.html")

@app.route("/cart")
def cart():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    c.execute("""
        SELECT cart.id, products.name, products.price, cart.quantity
        FROM cart
        JOIN products ON cart.product_id = products.id
    """)

    items = c.fetchall()

    total_amount = 0
    for item in items:
        total_amount += item[2] * item[3]

    conn.close()

    return render_template("cart.html", items=items, total=total_amount)

@app.route("/checkout")
def checkout():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    c.execute("""
        SELECT cart.id, products.name, products.price, cart.quantity
        FROM cart
        JOIN products ON cart.product_id = products.id
    """)

    items = c.fetchall()

    total_amount = 0
    for item in items:
        total_amount += item[2] * item[3]

    conn.close()

    return render_template("checkout.html", items=items, total=total_amount)

@app.route("/success")
def success():
    return render_template("success.html")


@app.route("/place_order", methods=["POST"])
def place_order():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    c.execute("""
        SELECT products.name, products.price, cart.quantity
        FROM cart
        JOIN products ON cart.product_id = products.id
    """)

    items = c.fetchall()

    for item in items:
        name = item[0]
        price = item[1]
        quantity = item[2]
        total = price * quantity

        c.execute("INSERT INTO orders (product_name, price, quantity, total) VALUES (?,?,?,?)",
                  (name, price, quantity, total))

    c.execute("DELETE FROM cart")

    conn.commit()
    conn.close()

    return redirect("/success")

@app.route("/orders")
def orders():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    c.execute("SELECT * FROM orders")
    all_orders = c.fetchall()

    conn.close()

    return render_template("orders.html", orders=all_orders)

@app.route("/register", methods=["POST"])
def register():
    name = request.form["name"]
    email = request.form["email"]
    password = request.form["password"]
    role = request.form["role"]

    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    c.execute("INSERT INTO users (name,email,password,role) VALUES(?,?,?,?)",
              (name, email, password, role))

    conn.commit()
    conn.close()

    return redirect("/")


# ==========================
# LOGIN
# ==========================

@app.route("/login", methods=["POST"])
def login():
    email = request.form["email"]
    password = request.form["password"]

    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    c.execute("SELECT * FROM users WHERE email=? AND password=?",
              (email, password))

    user = c.fetchone()  
    conn.close()

    if user:
        role = user[4]

        if role == "admin":
            return render_template("dashboard_admin.html")
        elif role == "vendor":
            return render_template("dashboard_vendor.html")
        else:
            return render_template("dashboard_user.html")
    else:
        return "Invalid Login"

# ==========================

if __name__ == "__main__":
    app.run(debug=True)


