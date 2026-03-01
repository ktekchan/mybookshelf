#!/usr/bin/env python3
"""Local web server for the reading scrapbook."""

from flask import Flask, jsonify, render_template, send_from_directory

import db

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/books")
def api_books():
    books = db.get_all_books()
    return jsonify(books)


@app.route("/photos/<filename>")
def serve_photo(filename):
    return send_from_directory(db.PHOTOS_DIR, filename)


if __name__ == "__main__":
    db.init_db()
    print("Opening your bookshelf at http://localhost:5001")
    app.run(debug=True, port=5001)
