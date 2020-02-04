import os
import random
from math import floor
from application import app as application

import sqlite3
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session.__init__ import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def  after_request(response):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Expires"] = 0
        response.headers["Pragma"] = "no-cache"
        return response

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


def get_quote():
    # Get random quote index to pull from DB
    # First we'll pull the full range of ids
    quote_id_range = list(range(1,95))

    # Then get the ids that have already been used
    used_quote_ids = session['quote_ids']

    # check if all quote ids have been used, if so we'll reset the used ids list
    if quote_id_range == used_quote_ids:
        session['quote_ids'] = []
        used_quote_ids = []

    # And create a list of available ids to use in the random.choice function
    available_quote_ids = list(set(quote_id_range) - set(used_quote_ids))


    # pull an unused quote id
    quote_id = random.choice(available_quote_ids)

    # Add quote_id to session index
    session['quote_ids'].append(quote_id)

    # Connect to SQLite database
    conn = sqlite3.connect("dick_or_don.db")
    db = conn.cursor()

    # Pull quote from DB with random index... how fun!!
    quote_selection = db.execute('''SELECT
                                           quote_id,
                                           quote
                                      FROM quotes
                                     WHERE quote_id = ?;''',
                                 (quote_id,))
    
    quote_selection = quote_selection.fetchone()
    quote = quote_selection[1]
    quote_id = quote_selection[0]
    conn.close()

    quote_data = [quote, quote_id]

    return quote_data


@app.route("/", methods=["GET"])
def index():
    # set variables to hold the total correct & total guesses variables
    session['total_correct'] = 0
    session['total_guesses'] = 0
    session['quote_ids'] = []
    return redirect("/form")


@app.route("/form", methods=["GET"])
def get_form():
    quote_data = get_quote()

    quote = quote_data[0]
    quote_id = quote_data[1]
    photo_id = quote_id % 15

    return render_template("form.html", quote=quote, quote_id=quote_id, photo_id=photo_id)

@app.route("/form", methods=["POST"])
def check_answer():
    if request.form.get("selection") == "refresh":
        return redirect("/form")

    selection = request.form.get("selection")
    quote = request.form.get("quote")
    quote_id = request.form.get("quote_id")

    # Connect to SQLite database
    conn = sqlite3.connect("dick_or_don.db")
    db = conn.cursor()

    utterer = db.execute('''SELECT
                                   utterer
                              FROM quotes
                             WHERE quote_id = ?;''',
                         (quote_id,))
    utterer = utterer.fetchone()
    utterer = utterer[0]
    conn.close()

    # map the selection to the utterer id stored in the SQLite DB
    selection_dict = {"Dick": 0, "Don": 1}
    selection = selection_dict[selection]

    # get the utterer name for presenting on the check page
    utterer_dict = {0: "Richard M Nixon", 1: "Donald J Trump"}
    utterer_name = utterer_dict[utterer]

    # update total number of guesses for tracking % correct
    session['total_guesses'] += 1
    total_guesses = session['total_guesses']

    # get a photo index for the correct/incorrect guess
    photo_index = random.randint(0,4)

    if selection == utterer:
        # update total correct for tracking % correct
        session['total_correct'] += 1
        total_correct = session['total_correct']
        percent_correct = floor(total_correct / total_guesses * 100)

        check_message = f'That is correct! This shit was said by {utterer_name}'

        # get photo of either Dick or Don to show on the check screen
        if utterer == 0:
            photo_id = f"dick-c-{photo_index}.jpeg"
        else:
            photo_id = f"don-c-{photo_index}.jpeg"
    else:
        total_correct = session['total_correct']
        percent_correct = floor(total_correct / total_guesses * 100)
        check_message = f'Wrong! This shit was said by {utterer_name}'

        # get photo of either Dick or Don to show on check screen
        if utterer == 0:
            photo_id = f"dick-i-{photo_index}.jpeg"
        else:
            photo_id = f"don-i-{photo_index}.jpeg"

    return render_template("check.html", quote=quote, check_message=check_message, total_correct=total_correct, percent_correct=percent_correct, photo_id=photo_id)


if __name__ == "__main__":
    app.debug = True
    app.run()