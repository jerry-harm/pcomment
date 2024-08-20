import os
import sys

from datetime import datetime

from flask import Flask, abort, redirect, request, render_template, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship


WIN = sys.platform.startswith('win')
if WIN:  # 如果是 Windows 系统，使用三个斜线
    prefix = 'sqlite:///'
else:  # 否则使用四个斜线
    prefix = 'sqlite:////'

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = prefix + os.path.join(app.root_path, 'data.db')
db = SQLAlchemy(app)

class Comment(db.Model):  
    id= mapped_column(Integer,primary_key=True)
    name = mapped_column(String(60),default='anonymous')
    content = mapped_column(Text,default='nothing...')
    date = mapped_column(DateTime,default=datetime.now,onupdate=datetime.now)
    replay_id = mapped_column(Integer,ForeignKey("comment.id"),nullable=True) # 空白时作为根comment

    def get_replays(self):
        # 查询并返回
        data=[]
        replays =  db.session.execute(db.select(Comment).filter_by(replay_id=self.id)).scalars()
        for replay in replays:
            print(replay.id)
            data.append(replay.to_dict())
        return data
        
    def to_dict(self):
        return {
                'id':self.id,
                'name':self.name,
                'content':self.content,
                'time':self.date,
                'replay':self.get_replays()
                }


@app.post("/post")
def post():
    comment=Comment(content=request.form.get('content'),name=request.form.get('name'))
    db.session.add(comment)
    db.session.commit()
    # 管理员创建根post
    abort(200)



@app.get("/comment/<int:id>")
def get_comment(id):
    post = db.get_or_404(Comment,id)

    data=post.get_replays()
    # 返回某个post的评论
    return render_template('base.html',comments=data,post=post)
    

@app.post("/comment/<int:id>")
def post_comment(id):
    # 评论给id
    post = db.get_or_404(Comment,id)
    print('1')
    comment = Comment(content=request.form.get('content'),replay_id=post.id,name=request.form.get('name'))
    db.session.add(comment)
    db.session.commit()
    
    # 返回这个comment所在的post
    return redirect(url_for('get_comment',id=post.id))

@app.route("/test")
def test():
    comment=Comment(content='content',name='name')
    db.session.add(comment)
    db.session.commit()
    # 管理员创建根post
    return "created"


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run()
