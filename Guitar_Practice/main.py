from flask import Flask, render_template, request, redirect, url_for, Blueprint
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_required, current_user
from sqlalchemy import desc, func
from datetime import datetime
from matplotlib.figure import Figure
import matplotlib.dates as mdates
from .models import sessions,tasks
from . import db


main = Blueprint('main', __name__)

@main.route('/')
def index():
    return redirect(url_for("auth.login"))

@main.route('/profile')
@login_required
def profile():
    return render_template('profile.html', name=current_user.name)


@main.get("/task_list")
def task_list():
    user_id = current_user.get_id()
    max_bpms = db.session.query(sessions.task_id, func.max(sessions.bpm).label("bpm")).filter(sessions.user_id == user_id).group_by(sessions.task_id).subquery()
    last_session = db.session.query(sessions.task_id, func.max(sessions.date).label("last_session_date")).filter(sessions.user_id == user_id).group_by(sessions.task_id).subquery()
    task_list = db.session.query(tasks.id, tasks.title, tasks.target_bpm, tasks.complete) \
            .filter(tasks.user_id == user_id) \
            .outerjoin(max_bpms, tasks.id == max_bpms.c.task_id) \
            .outerjoin(last_session, tasks.id == last_session.c.task_id) \
            .add_entity(max_bpms.c.bpm) \
            .add_entity(last_session.c.last_session_date) \
            .order_by(last_session.c.last_session_date) \
            .all()
    return render_template("tasks.html", task_list=task_list)

# @main.route("/add", methods=["POST"])
@main.post("/add")
def add():
    title = request.form.get("title")
    target_bpm = request.form.get("target_bpm")
    user_id = current_user.get_id()
    new_task = tasks(title=title, target_bpm = target_bpm, complete=False, user_id = user_id)
    db.session.add(new_task)
    db.session.commit()
    return redirect(url_for("main.task_list"))


@main.post("/delete")
def delete():
    task_id = request.form.get("task_id")
    task = db.session.query(tasks).filter(tasks.id == task_id).first()
    db.session.delete(task)
    db.session.commit()
    session = db.session.query(sessions).filter(sessions.task_id == task_id).all()
    for item in session:
        db.session.delete(item)
    db.session.commit()   

    return redirect(url_for("main.task_list"))


@main.post("/addsession")
def addsession():
    task_id = int(request.form.get("task_id"))
    date = datetime.strptime(request.form.get("date"), "%Y-%m-%d")
    bpm = int(request.form.get("bpm"))
    user_id = current_user.get_id()
    new_session = sessions(task_id=task_id, bpm=bpm, date=date, user_id=user_id)
    db.session.add(new_session)
    db.session.commit()
    return redirect(url_for("main.task_detail", task_id=task_id))


@main.post("/deletesession")
def deletesession():
    task_id = request.form.get("task_id")
    session_id = request.form.get("session_id")
    # todo = Todo.query.filter_by(id=todo_id).first()
    session = db.session.query(sessions).filter(sessions.id == session_id).first()
    db.session.delete(session)
    db.session.commit()

    today = datetime.today().strftime("%Y-%m-%d")
    #return render_template("task_detail.html", task=task, session_list = session_list, today = today, last_session = last_session)
    return redirect(url_for("main.task_detail", task_id = task_id))


@main.get("/task/<int:task_id>")
def task_detail(task_id):
    # todo = Todo.query.filter_by(id=todo_id).first()
    user_id = current_user.get_id()
    session_list = db.session.query(sessions).filter(sessions.task_id == task_id).filter(sessions.user_id == user_id).order_by(desc(sessions.date)).all()
    task = db.session.query(tasks).filter(tasks.id == task_id).filter(tasks.user_id == user_id).first()
    last_session = db.session.query(sessions).filter(sessions.task_id == task_id).filter(sessions.user_id == user_id).order_by(desc(sessions.date)).first()
    print(last_session)
    today = datetime.today().strftime("%Y-%m-%d")


    data = [[[session.date.year, session.date.month,session.date.day], session.bpm] for session in session_list]

    return render_template("task_detail.html", task=task, session_list = session_list, today = today, last_session = last_session, data=data)

