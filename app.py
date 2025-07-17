from flask import Flask, request, redirect, render_template, url_for
from flask_sqlalchemy import SQLAlchemy
import string, random

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# DB model
class URLMap(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    short_code = db.Column(db.String(8), unique=True, nullable=False)
    long_url = db.Column(db.String(2048), nullable=False)

# Generate unique short code
def generate_code(length=6):
    chars = string.ascii_letters + string.digits
    while True:
        code = ''.join(random.choices(chars, k=length))
        if not URLMap.query.filter_by(short_code=code).first():
            return code

# Create tables within application context
with app.app_context():
    db.create_all()

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        long_url = request.form['long_url']
        code = generate_code()
        new_entry = URLMap(short_code=code, long_url=long_url)
        db.session.add(new_entry)
        db.session.commit()
        return render_template('success.html', code=code)
    
    return render_template('index.html')

@app.route('/debug')
def debug_db():
    """Debug route to see all URLs in database"""
    urls = URLMap.query.all()
    return render_template('debug.html', urls=urls)

@app.route('/delete/<int:url_id>', methods=['POST'])
def delete_url(url_id):
    """Delete a URL from the database"""
    url = URLMap.query.get_or_404(url_id)
    db.session.delete(url)
    db.session.commit()
    return redirect('/debug')

@app.route('/<short_code>')
def redirect_short(short_code):
    link = URLMap.query.filter_by(short_code=short_code).first()
    if link:
        return redirect(link.long_url)
    return "Short URL not found", 404

if __name__ == '__main__':
    app.run(debug=True)