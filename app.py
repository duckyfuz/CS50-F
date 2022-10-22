import os
import spotipy

from spotipy.oauth2 import SpotifyOAuth
from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")



scope = "user-library-read"

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))

results = sp.current_user_saved_tracks()
for idx, item in enumerate(results['items']):
    track = item['track']
    print(idx, track['artists'][0]['name'], " – ", track['name'])



@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""

    # Create list of stocks owned
    list = db.execute("SELECT * FROM stocks WHERE userid = ? ORDER BY symbol", session["user_id"])

    # Find price of stocks (and total value)
    price_list = []
    totalv = 0
    for x in range(len(list)):
        temp = lookup(list[x]["symbol"])
        price_list.append(temp["price"])
        totalv += float(temp["price"]) * float(list[x]["quantity"])

    # Find cash balance
    cash = db.execute("SELECT cash FROM users WHERE id = ?", session["user_id"])

    return render_template("index.html", list=list, price_list=price_list, cash=cash, totalv=totalv)


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # If the symbol inputted is blank or does not exist
        if len(request.form.get("symbol")) == 0:
            return apology("must provide stock symbol", 400)

        # If the symbol inputted does not exist
        elif lookup(request.form.get("symbol")) == None:
            return apology("stock does not exist", 400)

        # If nothing was entered
        try:
            float(request.form.get("shares"))
        except ValueError:
            return apology("invalid input", 400)

        # If the number of shares is not positive
        if float(request.form.get("shares")) <= 0:
            return apology("shares must be positive", 400)

        # If the number of shares is not whole
        elif float(request.form.get("shares")) % 1 != 0:
            return apology("shares must be integer", 400)

        # Check if there is enough money
        list = lookup(request.form.get("symbol"))
        user = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])
        if float(user[0]['cash']) < float((list["price"] * float(request.form.get("shares")))):
            return apology("not enough funds", 400)

        # Getting the needed values
        symbol = request.form.get("symbol")
        quantity = int(request.form.get("shares"))
        price = float(list["price"])
        balance = float(user[0]['cash'])

        # Does the user already own that stock?
        rows = db.execute("SELECT * FROM stocks WHERE userid = ? AND symbol = ?", session["user_id"], symbol)

        # User owns that stock already
        if len(rows) == 1:

            # Add onto the current stock
            currentquantity = db.execute("SELECT * FROM stocks WHERE symbol = ? and userid = ?", symbol, session["user_id"])
            db.execute("UPDATE stocks SET quantity = ? WHERE symbol = ? AND userid = ?",
                       currentquantity[0]["quantity"] + quantity, symbol, session["user_id"])

        # User does not own that stock
        else:

            # Insert row into stocks table
            db.execute("INSERT INTO stocks (userid, symbol, quantity) VALUES (?, ?, ?)", session["user_id"], symbol, quantity)

        # Keep reference
        db.execute("INSERT INTO stocksref (userid, symbol, quantity, transactionprice, bought) VALUES (?, ?, ?, ?, ?)",
                   session["user_id"], symbol, quantity, price, "BUY")

        # Reduce the cash balance
        newbalance = balance - (quantity * price)
        db.execute("UPDATE users SET cash = ? WHERE id = ?", newbalance, session["user_id"])

        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("buy.html")


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""

    # Create list of stocks owned
    list = db.execute("SELECT * FROM stocksref WHERE userid = ? ORDER BY date DESC, time DESC", session["user_id"])

    return render_template("trans.html", list=list)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""
    if request.method == "POST":

        # Ensure ticker was submitted
        if not request.form.get("symbol"):
            return apology("must provide ticker", 400)

        # Getting values from lookup
        list = lookup(request.form.get("symbol"))

        # If invalid symbol how
        if not list:
            return apology("invalid ticker", 400)

        return render_template("quoted.html", list=list)

    else:
        return render_template("quote.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 400)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username does not already exist
        if len(rows) == 1:
            return apology("username already exists", 400)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 400)

        # Ensure passwords match
        elif not request.form.get("password") == request.form.get("confirmation"):
            return apology("passwords must match", 400)

        # Add new user into database
        db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", request.form.get("username"),
                   generate_password_hash(request.form.get("password")))

        return redirect("/confirmation")

    else:
        return render_template("register.html")


@app.route("/confirmation")
def confirm():
    return render_template("confirmation.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # If nothing was entered
        try:
            float(request.form.get("shares"))
        except ValueError:
            return apology("invalid input", 400)

        # If the number of shares is not positive
        if float(request.form.get("shares")) <= 0:
            return apology("shares must be positive", 400)

        # If the number of shares is not whole
        elif float(request.form.get("shares")) % 1 != 0:
            return apology("shares must be integer", 400)

        # Does the user already own that stock?
        symbol = request.form.get("symbol")
        rows = db.execute("SELECT * FROM stocks WHERE userid = ? AND symbol = ?", session["user_id"], symbol)

        # If user somehow does not own the stock
        if len(rows) != 1:
            return apology("cannot sell what you don't have", 400)

        # User owns that stock
        else:

            list = lookup(request.form.get("symbol"))
            user = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])
            # Getting the needed values
            quantity = int(request.form.get("shares"))
            price = float(list["price"])
            balance = float(user[0]['cash'])

            # Remove from the current stock
            currentquantity = db.execute("SELECT * FROM stocks WHERE symbol = ? and userid = ?", symbol, session["user_id"])

            if currentquantity[0]["quantity"] < quantity:
                return apology("not enough stocks to sell", 400)

            else:
                db.execute("UPDATE stocks SET quantity = ? WHERE symbol = ? AND userid = ?",
                           currentquantity[0]["quantity"] - quantity, symbol, session["user_id"])

                # Keep reference
                db.execute("INSERT INTO stocksref (userid, symbol, quantity, transactionprice, bought) VALUES (?, ?, ?, ?, ?)",
                           session["user_id"], symbol, quantity, price, "SELL")

            # Increase the cash balance
            newbalance = balance + (quantity * price)
            db.execute("UPDATE users SET cash = ? WHERE id = ?", newbalance, session["user_id"])

        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:

        # Getting the list of stocks
        rows = db.execute("SELECT * FROM stocks WHERE userid = ? ORDER BY symbol", session["user_id"])
        stockslist = []
        for x in range(len(rows)):
            stockslist.append(rows[x]["symbol"])

        return render_template("sell.html", stockslist=stockslist)


@app.route("/change", methods=["GET", "POST"])
@login_required
def change():
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure passwords are submitted
        if not request.form.get("password"):
            return apology("must provide old password", 400)
        elif not request.form.get("newpass"):
            return apology("must provide new password", 400)
        elif not request.form.get("newpassconfirm"):
            return apology("must confirm new password", 400)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])
        # Check if old pass is correct
        if not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("old password is incorect", 403)

        # Ensure passwords match
        elif not request.form.get("newpass") == request.form.get("newpassconfirm"):
            return apology("new passwords must match", 400)

        # SUbmit changed password
        else:
            db.execute("UPDATE users SET hash = ? WHERE id = ?",
                       generate_password_hash(str(request.form.get("newpass"))), session["user_id"])

        return render_template("confirmation2.html")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("change.html")
