from flask import Flask
import sqlite3

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello World!'

@app.route('/post/<name>', methods=['POST'])
def get_post(name):
    return f"{name}"

if __name__ == '__main__':
    app.run()