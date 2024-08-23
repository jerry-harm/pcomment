import os
import sys

from datetime import datetime

from flask import Flask, abort, redirect, request, render_template, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

import click

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
    title = mapped_column(String(300),nullable=True)
    content = mapped_column(Text,default='nothing...')
    date = mapped_column(DateTime,default=datetime.now)
    like = mapped_column(Integer,default=0)
    dislike = mapped_column(Integer,default=0)
    replay_id = mapped_column(Integer,ForeignKey("comment.id"),nullable=True) # 空白时作为根comment

    def get_replays(self):
        # 查询并返回
        data=[]
        replays =  db.session.execute(db.select(Comment).filter_by(replay_id=self.id).order_by(Comment.date)).scalars()
        for replay in replays:
            data.append(replay.to_dict())
        return data
        
    def to_dict(self):
        return {
                'id':self.id,
                'title':self.title,
                'name':self.name,
                'like':self.like,
                'dislike':self.dislike,
                'content':self.content,
                'date':self.date,
                'replay':self.get_replays()
                }


@app.get("/")
def index():
    try:
        posts = db.session.execute(db.select(Comment).filter_by(replay_id=None).order_by(Comment.date)).scalars()
        return render_template("index.html",comments=posts)
    except Exception:
        db.create_all()
        return 'No table'

@app.get("/post/<title>/<content>")
def get_post(title,content):
    post = db.session.execute(db.select(Comment).filter_by(replay_id=None).filter_by(title=title)).scalar()
    if not post:
        post = Comment(title=title,name='jestar',content=content)
        db.session.add(post)
        db.session.commit()
    return redirect(url_for('get_comment',id=post.id))        

@app.get("/like/<int:id>")
def like(id):
    # 
    comment = db.get_or_404(Comment,id)
    comment.like+=1
    db.session.commit()
    reference = request.headers.get('Referer')
    if reference:
        return redirect(reference)
    return redirect(url_for('get_comment',id=id))

@app.get("/dislike/<int:id>")
def dislike(id):
    comment = db.get_or_404(Comment,id)
    comment.dislike+=1
    db.session.commit()
    reference = request.headers.get('Referer')
    if reference:
        return redirect(reference)
    return redirect(url_for('get_comment',id=comment.id))


@app.get("/comment/<int:id>")
def get_comment(id):
    post = db.get_or_404(Comment,id)
    data=post.get_replays()
    # 返回某个post的评论
    return render_template('comment.html',comments=data,post=post)
    

import markdown
import markupsafe

@app.post("/comment/<int:id>")
def post_comment(id):
    # 评论给id
    post = db.get_or_404(Comment,id)
    if not request.form.get('content'):
        abort(400)
    if request.form.get('name'):
        name = request.form.get('name')
    else:
        name = None
    comment = Comment(
        content=markdown.markdown(markupsafe.Markup.escape(request.form.get('content'))),              
        replay_id=post.id,name=name,title=request.form.get('title')
        )
    db.session.add(comment)
    db.session.commit()
    reference = request.headers.get('Referer')
    if reference:
        return redirect(reference)
    return redirect(url_for('get_comment',id=post.id))


@app.cli.command('create',help='add a comment')
@click.argument("content")
@click.option('--title',default=None)
@click.option('--name',default=None)
@click.option('--replay_id',default=None)
def create_post(content,title,name,replay_id):
    with app.app_context():
        db.create_all()
        comment=Comment(content=content,name=name,title=title,replay_id=replay_id)
        db.session.add(comment)
        db.session.commit()
    print('created')

@app.cli.command('change',help='change and show')
@click.argument("id")
@click.option('--content',default=None)
@click.option('--title',default=None)
@click.option('--name',default=None)
@click.option('--replay_id',default=None)
def change_post(id,content,title,name,replay_id):
    with app.app_context():
        comment=db.get_or_404(Comment,id)
        if content:
            comment.content=content
        if title:
            comment.title=title
        if name:
            comment.name=name
        if replay_id:
            comment.replay_id=replay_id
        print(comment.__dict__)
        db.session.commit()
    print('modified')

@app.cli.command('del',help='delete a comment')
@click.argument("id")
def change_post(id):
    with app.app_context():
        comment=db.get_or_404(Comment,id)
        print(comment.__dict__)
        db.session.delete(comment)
    print('modified')

@app.cli.command('post',help='add new post')
@click.argument('title')
@click.argument("content",default='post')
@click.argument('name',default='admin')
def create_post(content,title,name):
    with app.app_context():
        db.create_all()
        searched = db.session.execute(db.select(Comment).filter_by(replay_id=None).filter_by(title=title)).scalar()
        if searched:
            print('error')
        else:
            comment=Comment(content=content,name=name,title=title)
            db.session.add(comment)
            db.session.commit()
            print('added')

@app.cli.command('check',help='check all comments')
def create_post():
    with app.app_context():
        searched = db.session.execute(db.select(Comment).filter(Comment.replay_id != None)).scalars()
        for comment in searched:
            print(comment.name+':'+comment.title+'to'+str(comment.replay_id))
            print(comment.content)
            print('\n')

@app.cli.command('init',help='init db')
def create_post():
    with app.app_context():
        db.create_all()
    print('created')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run()
