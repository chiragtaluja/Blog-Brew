# app.py
from flask import Flask, render_template, request, redirect, url_for, session, flash
from models import db, BlogPost, User
import os

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'default_dev_key')  # Replace 'default_dev_key' in production
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
    'DATABASE_URI', 'mysql+pymysql://root:admin123@localhost:3306/flask_blog')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    posts = BlogPost.query.all()
    return render_template('index.html', posts=posts)

@app.route('/add', methods=['GET', 'POST'])
def add_post():
    if 'user_id' not in session:
        flash('You must be logged in to add a blog.')
        return redirect(url_for('login'))

    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        author = request.form['author']
        user_id = session['user_id']

        new_post = BlogPost(title=title, content=content, author=author, user_id=user_id)
        db.session.add(new_post)
        db.session.commit()
        flash('Blog posted successfully.')
        return redirect(url_for('index'))

    return render_template('add_post.html')

@app.route('/edit/<int:post_id>', methods=['GET', 'POST'])
def edit_post(post_id):
    post = BlogPost.query.get_or_404(post_id)
    if post.user_id != session.get('user_id'):
        flash("You don't have permission to edit this post.")
        return redirect(url_for('index'))

    if request.method == 'POST':
        post.title = request.form['title']
        post.content = request.form['content']
        post.author = request.form['author']
        db.session.commit()
        flash('Post updated successfully.')
        return redirect(url_for('index'))

    return render_template('edit_post.html', post=post)

@app.route('/delete/<int:post_id>', methods=['POST'])
def delete_post(post_id):
    post = BlogPost.query.get_or_404(post_id)
    if post.user_id != session.get('user_id'):
        flash("You don't have permission to delete this post.")
        return redirect(url_for('index'))

    db.session.delete(post)
    db.session.commit()
    flash('Post deleted.')
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if User.query.filter_by(username=username).first():
            flash('Username already exists!')
            return redirect(url_for('register'))

        new_user = User(username=username)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        flash('Registered successfully!')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['username'] = user.username
            flash('Login successful')
            return redirect(url_for('index'))
        else:
            flash('Invalid credentials')

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully.')
    return redirect(url_for('login'))

@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404

@app.route('/post/<int:post_id>')
def view_post(post_id):
    post = BlogPost.query.get_or_404(post_id)
    return render_template('view_post.html', post=post)


if __name__ == '__main__':
    app.run(debug=False) 
