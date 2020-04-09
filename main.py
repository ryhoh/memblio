from flask import Flask, render_template, request, redirect, url_for, Response

from src import query_all


app = Flask(__name__)


@app.route("/", methods=["GET"])
def main_page():
    books = query_all()
    return render_template("index.html", books=books)


if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=48398, threaded=True)
