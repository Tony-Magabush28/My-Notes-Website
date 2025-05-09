from flask import render_template, redirect, url_for, flash, request
from app import app, db
from app.forms import RegisterForm, LoginForm, NoteForm
from app.models import User, Note
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        hashed_pw = generate_password_hash(form.password.data)
        user = User(username=form.username.data, password=hashed_pw)
        db.session.add(user)
        db.session.commit()
        flash('Account created! Please log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            return redirect(url_for('dashboard'))
        flash('Invalid credentials', 'danger')
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    notes = Note.query.filter_by(user_id=current_user.id).all()
    return render_template('dashboard.html', notes=notes)

@app.route('/add', methods=['GET', 'POST'])
@login_required
def add_note():
    form = NoteForm()
    if form.validate_on_submit():
        note = Note(content=form.content.data, user_id=current_user.id)
        db.session.add(note)
        db.session.commit()
        return redirect(url_for('dashboard'))
    return render_template('add_note.html', form=form)

@app.route('/delete/<int:note_id>')
@login_required
def delete_note(note_id):
    note = Note.query.get_or_404(note_id)
    if note.user_id != current_user.id:
        flash("Unauthorized", "danger")
        return redirect(url_for('dashboard'))
    db.session.delete(note)
    db.session.commit()
    return redirect(url_for('dashboard'))

@app.route('/edit/<int:note_id>', methods=['GET', 'POST'])
@login_required
def edit_note(note_id):
    note = Note.query.get_or_404(note_id)
    if note.user_id != current_user.id:
        flash("Unauthorized", "danger")
        return redirect(url_for('dashboard'))

    form = NoteForm()
    if request.method == 'GET':
        form.content.data = note.content

    if form.validate_on_submit():
        note.content = form.content.data
        db.session.commit()
        flash('Note updated successfully!', 'success')
        return redirect(url_for('dashboard'))

    return render_template('edit_note.html', form=form)

