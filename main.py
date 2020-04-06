from flask import Flask, render_template, request, redirect, url_for, Response


app = Flask(__name__)


@app.route("/", methods=["GET"])
def main_page():
    return render_template("index.html")


if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', threaded=True)
