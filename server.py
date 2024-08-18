from flask import Flask
import sqlite3

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello World!'

@app.route('/post/<id>', methods=['POST'])
def get_post(id):
    return f"{id}"

if __name__ == '__main__':
    app.run()