from flask import (
    Flask,
    render_template,
    request,
    redirect,
    flash,
    session,
    render_template_string
)
import mysql.connector
import os

app = Flask(__name__)

# =========================================================
# FLASK SECRET KEY
# =========================================================

app.secret_key = os.environ.get(
    "FLASK_SECRET_KEY",
    "expense_tracker_secret"
)


# =========================================================
# DATABASE CONNECTION
# =========================================================

def get_connection():
    return mysql.connector.connect(
        host="gateway01.ap-southeast-1.prod.alicloud.tidbcloud.com",
        port=4000,
        user="2Fg93V8C4Zpwxen.root",
        password=os.environ["TIDB_PASSWORD"],
        database="expense_tracker",
        ssl_verify_cert=True,
        ssl_verify_identity=True
    )


# =========================================================
# HOME
# =========================================================

@app.route("/")
def index():
    return render_template("index.html")


# =========================================================
# REGISTER
# =========================================================

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        try:
            fullname = request.form["fullname"]
            email = request.form["email"]
            password = request.form["password"]
            confirm_password = request.form["confirm_password"]

            if password != confirm_password:
                flash(
                    "Password and Confirm Password do not match!",
                    "danger"
                )
                return redirect("/register")

            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute(
                "SELECT * FROM users WHERE email=%s",
                (email,)
            )

            user = cursor.fetchone()

            if user:
                cursor.close()
                conn.close()

                flash(
                    "Email already exists!",
                    "warning"
                )
                return redirect("/register")

            query = """
                INSERT INTO users(fullname, email, password)
                VALUES(%s, %s, %s)
            """

            cursor.execute(
                query,
                (fullname, email, password)
            )

            conn.commit()

            cursor.close()
            conn.close()

            flash(
                "Registration Successful!",
                "success"
            )

            return redirect("/login")

        except Exception as e:
            print("REGISTER ERROR:", e)

            return f"""
                <h2>Registration Error</h2>
                <p>{str(e)}</p>
            """, 500

    return render_template("register.html")


# =========================================================
# LOGIN
# =========================================================

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        try:
            email = request.form["email"]
            password = request.form["password"]

            conn = get_connection()
            cursor = conn.cursor(dictionary=True)

            query = """
                SELECT *
                FROM users
                WHERE email=%s AND password=%s
            """

            cursor.execute(
                query,
                (email, password)
            )

            user = cursor.fetchone()

            cursor.close()
            conn.close()

            if user:

                session["user_id"] = user["id"]
                session["fullname"] = user["fullname"]

                flash(
                    "Login Successful!",
                    "success"
                )

                return redirect("/dashboard")

            else:

                flash(
                    "Invalid Email or Password!",
                    "danger"
                )

                return redirect("/login")

        except Exception as e:
            print("LOGIN ERROR:", e)

            return f"""
                <h2>Login Error</h2>
                <p>{str(e)}</p>
            """, 500

    return render_template("login.html")


# =========================================================
# DASHBOARD
# =========================================================

@app.route("/dashboard")
def dashboard():

    if "user_id" not in session:
        return redirect("/login")

    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        # Total Income
        cursor.execute("""
            SELECT SUM(amount) AS total_income
            FROM transactions
            WHERE user_id=%s
            AND type='Income'
        """, (session["user_id"],))

        income = cursor.fetchone()

        # Total Expense
        cursor.execute("""
            SELECT SUM(amount) AS total_expense
            FROM transactions
            WHERE user_id=%s
            AND type='Expense'
        """, (session["user_id"],))

        expense = cursor.fetchone()

        # Recent Transactions
        cursor.execute("""
            SELECT category, amount, type, transaction_date
            FROM transactions
            WHERE user_id=%s
            ORDER BY transaction_date DESC
        """, (session["user_id"],))

        transactions = cursor.fetchall()

        cursor.close()
        conn.close()

        total_income = income["total_income"] or 0
        total_expense = expense["total_expense"] or 0
        balance = total_income - total_expense

        return render_template(
            "dashboard.html",
            fullname=session["fullname"],
            total_income=total_income,
            total_expense=total_expense,
            balance=balance,
            transactions=transactions
        )

    except Exception as e:
        print("DASHBOARD ERROR:", e)

        return f"""
            <h2>Dashboard Error</h2>
            <p>{str(e)}</p>
        """, 500


# =========================================================
# ADD INCOME
# =========================================================

@app.route("/add_income", methods=["GET", "POST"])
def add_income():

    if "user_id" not in session:
        return redirect("/login")

    if request.method == "POST":

        try:
            category = request.form["category"]
            amount = request.form["amount"]
            description = request.form["description"]
            transaction_date = request.form["transaction_date"]

            conn = get_connection()
            cursor = conn.cursor()

            query = """
                INSERT INTO transactions
                (
                    user_id,
                    type,
                    category,
                    amount,
                    description,
                    transaction_date
                )
                VALUES (%s, %s, %s, %s, %s, %s)
            """

            cursor.execute(
                query,
                (
                    session["user_id"],
                    "Income",
                    category,
                    amount,
                    description,
                    transaction_date
                )
            )

            conn.commit()

            cursor.close()
            conn.close()

            flash(
                "Income Added Successfully!",
                "success"
            )

            return redirect("/dashboard")

        except Exception as e:
            print("ADD INCOME ERROR:", e)

            return f"""
                <h2>Add Income Error</h2>
                <p>{str(e)}</p>
            """, 500

    return render_template("add_income.html")


# =========================================================
# ADD EXPENSE
# =========================================================

@app.route("/add_expense", methods=["GET", "POST"])
def add_expense():

    if "user_id" not in session:
        return redirect("/login")

    if request.method == "POST":

        try:
            category = request.form["category"]
            amount = request.form["amount"]
            description = request.form["description"]
            transaction_date = request.form["transaction_date"]

            conn = get_connection()
            cursor = conn.cursor()

            query = """
                INSERT INTO transactions
                (
                    user_id,
                    type,
                    category,
                    amount,
                    description,
                    transaction_date
                )
                VALUES (%s, %s, %s, %s, %s, %s)
            """

            cursor.execute(
                query,
                (
                    session["user_id"],
                    "Expense",
                    category,
                    amount,
                    description,
                    transaction_date
                )
            )

            conn.commit()

            cursor.close()
            conn.close()

            flash(
                "Expense Added Successfully!",
                "success"
            )

            return redirect("/dashboard")

        except Exception as e:
            print("ADD EXPENSE ERROR:", e)

            return f"""
                <h2>Add Expense Error</h2>
                <p>{str(e)}</p>
            """, 500

    return render_template("add_expense.html")


# =========================================================
# TRANSACTIONS
# =========================================================

@app.route("/transactions", methods=["GET", "POST"])
def transactions():

    if "user_id" not in session:
        return redirect("/login")

    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        query = """
            SELECT *
            FROM transactions
            WHERE user_id=%s
            ORDER BY transaction_date DESC
        """

        cursor.execute(
            query,
            (session["user_id"],)
        )

        transactions_data = cursor.fetchall()

        cursor.close()
        conn.close()

        return render_template(
            "transactions.html",
            fullname=session["fullname"],
            transactions=transactions_data
        )

    except Exception as e:
        print("TRANSACTIONS ERROR:", e)

        return f"""
            <h2>Transactions Error</h2>
            <p>{str(e)}</p>
        """, 500


# =========================================================
# PROFILE
# =========================================================

@app.route("/profile", methods=["GET", "POST"])
def profile():

    if "user_id" not in session:
        return redirect("/login")

    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        if request.method == "POST":

            fullname = request.form["fullname"]
            email = request.form["email"]

            cursor.execute("""
                UPDATE users
                SET fullname=%s,
                    email=%s
                WHERE id=%s
            """, (
                fullname,
                email,
                session["user_id"]
            ))

            conn.commit()

            session["fullname"] = fullname

            flash(
                "Profile Updated Successfully!",
                "success"
            )

        cursor.execute("""
            SELECT *
            FROM users
            WHERE id=%s
        """, (session["user_id"],))

        user = cursor.fetchone()

        cursor.close()
        conn.close()

        return render_template(
            "profile.html",
            user=user
        )

    except Exception as e:
        print("PROFILE ERROR:", e)

        return f"""
            <h2>Profile Error</h2>
            <p>{str(e)}</p>
        """, 500


# =========================================================
# LOGOUT
# =========================================================

@app.route("/logout")
def logout():

    session.clear()

    flash(
        "Logged out successfully!",
        "success"
    )

    return redirect("/login")


# =========================================================
# DATABASE TEST
# =========================================================

@app.route("/test-db")
def test_db():

    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT 1")

        result = cursor.fetchone()

        cursor.close()
        conn.close()

        return f"""
            <h2>Database Connection Successful!</h2>
            <p>Result: {result}</p>
        """

    except Exception as e:

        return f"""
            <h2>Database Connection Failed</h2>
            <p>{str(e)}</p>
        """, 500

# =========================================================
# RUN
# =========================================================

if __name__ == "__main__":
    app.run(debug=True)
