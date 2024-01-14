from flask import Flask, render_template, request, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import secrets
from datetime import datetime
from flask_migrate import Migrate

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'  # SQLiteデータベースのファイル名
app.config['SECRET_KEY'] = secrets.token_hex(16) 
db = SQLAlchemy(app)
migrate = Migrate(app, db)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email_address = db.Column(db.String(120), unique=True, nullable=True)
    password_hash = db.Column(db.String(128), nullable=False)
    comments = db.relationship('Comment', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.String(80), nullable=False)
    date = db.Column(db.DateTime, default=datetime.now())


@app.route('/')
def input():
    return render_template('input.html') 

@app.route('/register')
def register():
    return render_template('register.html') 

@app.route('/signup' , methods=["post"])
def signup():
    db.create_all()
    username = request.form.get('username')
    password = request.form.get('password')
    confirm_password = request.form.get('confirm_password')
    if password == confirm_password:
        password_hash = generate_password_hash(password)
        new_user = User(username=username, password_hash = password_hash)
        
        db.session.add(new_user)
        db.session.commit()
        return render_template('home.html') 
    return 'passwordが一致しません'

@app.route('/login' , methods=["post"])
def login():
    username = request.form.get('username')
    password = request.form.get('password')
    user = User.query.filter_by(username=username).first()
    if user and check_password_hash(user.password_hash, password):
        session['username'] = username 
        # return render_template('home.html', username=username)
        return redirect(url_for('home'))
    else:
        return 'Invalid username or password'

@app.route('/logout')
def logout():
    session.pop('username', None)  # セッションからユーザー名を削除
    print('session',session)
    return render_template('input.html')

@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/comment' , methods=["post"])
def comment():
    db.create_all()
    content = request.form.get('contents')
    user_id = User.query.filter_by(username=session['username']).first().id
    new_comment = Comment(content=content, user_id=user_id)
    db.session.add(new_comment)
    db.session.commit()
    print(new_comment)
    return redirect(url_for('mypage'))

@app.route('/mypage')
def mypage():
    user = User.query.filter_by(username=session['username']).first()
    comments = user.comments
    for comment in comments:
        print(comment.content)
    return render_template('mypage.html', user=user, comments=comments)

@app.route('/user_detail' , methods=["post"])
def user_detail():
    email_address = request.form.get('email_address')
    existing_user = User.query.filter_by(username=session['username']).first()
    existing_user.email_address = email_address
    db.session.commit()
    return redirect(url_for('mypage'))

# with app.app_context():
#     db.create_all()
#     new_user = User(username='b')
#     db.session.add(new_user)
#     db.session.commit()

if __name__ == '__main__':
    app.run(debug=True)