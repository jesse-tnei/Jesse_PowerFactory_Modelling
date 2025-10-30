import os
from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/loadflow')
def loadflow():
    return render_template('loadflow.html')


@app.route('/EDCM')
def start_edcm():
    return render_template('edcm-dashboard.html')

def start_web_server(host='localhost', port=5000):
    """Start the Flask web server"""
    app.run(host=host, port=port, debug=False, threaded=True, use_reloader=False)

if __name__ == '__main__':
    app.run(host='localhost', port=5000, debug=True)
    print("Completed running Flask app.")
