from flask import Flask,render_template
import sqlite3

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello World!'

@app.route('/post/<id>', methods=['POST'])
def get_post(id):
    return f"{id}"

@app.route('/test')
def test():
    data=[
        {'name':'1',
        'content':'test1',
        'time':'1',
        'replays':[
            {'name':'2',
        'content':'test2',
        'time':'2',
        'replays':[]
        }
        ]},
        {'name':'3',
        'content':'test3',
        'time':'3',
        'replays':[
            {'name':'4',
        'content':'test4',
        'time':'4',
        'replays':[]
        }
        ]}
    ]
    return render_template('base.html',comments=data,post='test')


if __name__ == '__main__':
    app.run()