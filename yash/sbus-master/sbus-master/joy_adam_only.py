# Import necessary modules from Flask and requests libraries
from flask import Flask, render_template, request
import requests

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('joy_adam_only.html')


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=6006, debug=True) #OG