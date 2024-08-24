from flask import render_template, redirect, url_for, flash, request, abort
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
import os

from . import db
from .models import User, Trade
from . import create_app

app = create_app()


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


@app.route('/')
@login_required
def index():
    trades = Trade.query.filter_by(user_id=current_user.id).all()
    return render_template('index.html', trades=trades)


@app.route('/add_trade', methods=['GET', 'POST'])
@login_required
def add_trade():
    if request.method == 'POST':
        trade_name = request.form['trade_name']
        entry_price = request.form['entry_price']
        exit_price = request.form['exit_price']
        result = request.form['result']
        notes = request.form['notes']
        chart = request.files['chart']

        if chart and allowed_file(chart.filename):
            filename = secure_filename(chart.filename)
            chart.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        new_trade = Trade(
            name=trade_name,
            entry_price=entry_price,
            exit_price=exit_price,
            result=result,
            notes=notes,
            chart_filename=filename,
            user_id=current_user.id
        )

        db.session.add(new_trade)
        db.session.commit()
        flash('Trade added successfully!', 'success')
        return redirect(url_for('index'))

    return render_template('add_trade.html')


@app.route('/trade/<int:trade_id>')
@login_required
def trade_details(trade_id):
    trade = Trade.query.get_or_404(trade_id)
    if trade.user_id != current_user.id:
        abort(403)  # Forbidden

    return render_template('trade_details.html', trade=trade)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        user = User(username=username, email=email)
        user.set_password(password)

        db.session.add(user)
        db.session.commit()
        login_user(user)
        flash('Registration successful!', 'success')
        return redirect(url_for('index'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user, remember=True)
            flash('Login successful!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Login unsuccessful. Check email and password.', 'danger')

    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))
