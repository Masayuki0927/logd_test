from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'  # SQLiteデータベースのファイル名
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

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
    password_hash = generate_password_hash(password)
    new_user = User(username=username, password_hash = password_hash)
    db.session.add(new_user)
    db.session.commit()
    return render_template('home.html') 

@app.route('/login' , methods=["post"])
def login():
    username = request.form.get('username')
    password = request.form.get('password')
    user = User.query.filter_by(username=username).first()
    if user and check_password_hash(user.password_hash, password):
        return render_template('home.html', username=username)
    else:
        return 'Invalid username or password'
    # new_user = User(username=username, password = password)
    # db.session.add(new_user)
    # db.session.commit()

# with app.app_context():
#     db.create_all()
#     new_user = User(username='b')
#     db.session.add(new_user)
#     db.session.commit()

if __name__ == '__main__':
    app.run(debug=False)