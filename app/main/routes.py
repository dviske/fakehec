from flask import jsonify, request, flash, redirect, url_for, render_template
from flask_login import current_user, login_user, logout_user, login_required
import sqlalchemy as sa
from app import db
from app.models import Collector, Message
from app.main.forms import LoginForm
from uuid import uuid4
from app.main import bp

@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
def index():
  if current_user.is_authenticated:
    return redirect(url_for('main.view_collector'))

  form = LoginForm()
  if form.validate_on_submit():
    user = db.session.scalar(
      sa.select(Collector).where(Collector.name == form.name.data))

    if user is None:
      collector = Collector(name=form.name.data, token=str(uuid4()))
      collector.set_password(form.password.data)
      db.session.add(collector)
      db.session.commit()
      flash("Collector created")
      login_user(collector)
      return redirect(url_for('main.view_collector'))
    elif user is not None:
      if not user.check_password(form.password.data):
        print('Invalid password')
        flash("Invalid password")
        return redirect(url_for('main.index'))

    login_user(user, remember=form.remember_me.data)
    return redirect(url_for('main.index'))
    
  return render_template('index.html', title='Home', form=form)

@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@bp.route('/collector', methods=['GET'])
@login_required
def view_collector():
   query = sa.select(Message).order_by(Message.received_at.desc())
   messages = db.session.scalars(query).all()
   return render_template('view_collector.html', messages=messages)

@bp.route('/regenerate', methods=['GET'])
def regenerate():
    if current_user.is_authenticated:
        collector = db.session.scalar(
            sa.select(Collector).where(Collector.name == current_user.name))
        collector.token = str(uuid4())
        db.session.commit()
        flash("Token regenerated")
    else:
        flash("You need to be logged in to do this")
    return redirect(url_for('main.view_collector'))

@bp.route('/delete', methods=['GET'])
def delete():
    if current_user.is_authenticated:
        collector = db.session.scalar(
            sa.select(Collector).where(Collector.name == current_user.name))
        messages = db.session.scalars(
            sa.select(Message).where(Message.collector_id == collector.id)).all()
        for message in messages:
            db.session.delete(message)
        db.session.commit()
        db.session.delete(collector)
        db.session.commit()
        flash("Collector deleted")
    else:
        flash("You need to be logged in to do this")
    return redirect(url_for('main.index'))