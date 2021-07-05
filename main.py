from flask import Flask, render_template, request, redirect, url_for, Response

from src import select_all, access_book_info, insert_book


app = Flask(__name__)


@app.route("/", methods=["GET"])
def main_page():
    books = select_all()
    return render_template("index.html", books=books)


@app.route("/register/book/", methods=["POST"])
def register_book():
    info = access_book_info(isbn=request.form['ISBN'])
    insert_book(info=info, media=request.form['Media'])
    return "registered!\n"


if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=48398, threaded=True)
