from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc, func
from datetime import datetime

app = Flask(__name__)

# /// = relative path, //// = absolute path
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

app.app_context().push()


class tasks(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    target_bpm = db.Column(db.Integer)
    complete = db.Column(db.Boolean)

class sessions(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer)
    date = db.Column(db.Date)
    bpm = db.Column(db.Integer)
    duration = db.Column(db.Time)


db.create_all()


@app.get("/")
def home():

    max_bpms = db.session.query(sessions.task_id, func.max(sessions.bpm).label("bpm")).group_by(sessions.task_id).subquery()
    task_list = db.session.query(tasks.id, tasks.title, tasks.target_bpm, tasks.complete) \
            .outerjoin(max_bpms, tasks.id == max_bpms.c.task_id).add_entity(max_bpms.c.bpm).all()
    return render_template("base.html", task_list=task_list)

# @app.route("/add", methods=["POST"])
@app.post("/add")
def add():
    title = request.form.get("title")
    target_bpm = request.form.get("target_bpm")
    new_task = tasks(title=title, target_bpm = target_bpm, complete=False)
    db.session.add(new_task)
    db.session.commit()
    return redirect(url_for("home"))

@app.post("/addsession")
def addsession():
    date = request.form.get("date")
    bpm = request.form.get("bpm")
    task_id = request.form.get("task_id")
    new_session = sessions(task_id=int(task_id), bpm=int(bpm), date=datetime.strptime(date, "%Y-%m-%d"))
    db.session.add(new_session)
    db.session.commit()
    return redirect(url_for("task", task_id=task_id))

@app.post("/delete")
def delete():
    task_id = request.form.get("task_id")
    task = db.session.query(tasks).filter(tasks.id == task_id).first()
    db.session.delete(task)
    db.session.commit()
    session = db.session.query(sessions).filter(sessions.task_id == task_id).all()
    for item in session:
        db.session.delete(item)
    db.session.commit()   

    return redirect(url_for("home"))

@app.post("/deletesession")
def deletesession():
    task_id = request.form.get("task_id")
    session_id = request.form.get("session_id")
    # todo = Todo.query.filter_by(id=todo_id).first()
    session = db.session.query(sessions).filter(sessions.id == session_id).first()
    db.session.delete(session)
    db.session.commit()
    session_list = db.session.query(sessions).filter(sessions.task_id == task_id).all()
    task = db.session.query(tasks).filter(tasks.id == task_id).first()
    db.session.commit()
    last_session = db.session.query(sessions).filter(sessions.task_id == task_id).order_by(desc(sessions.bpm)).first()

    today = datetime.today().strftime("%Y-%m-%d")
    return render_template("task.html", task=task, session_list = session_list, today = today, last_session = last_session)

@app.get("/task/<int:task_id>")
def task(task_id):
    # todo = Todo.query.filter_by(id=todo_id).first()
    session_list = db.session.query(sessions).filter(sessions.task_id == task_id).all()
    task = db.session.query(tasks).filter(tasks.id == task_id).first()
    db.session.commit()
    last_session = db.session.query(sessions).filter(sessions.task_id == task_id).order_by(desc(sessions.id)).first()

    today = datetime.today().strftime("%Y-%m-%d")
    return render_template("task.html", task=task, session_list = session_list, today = today, last_session = last_session)

