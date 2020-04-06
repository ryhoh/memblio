from flask import Flask, render_template, request, redirect, url_for, Response


app = Flask(__name__)


@app.route("/", methods=["GET"])
def main_page():
    return render_template("index.html")
