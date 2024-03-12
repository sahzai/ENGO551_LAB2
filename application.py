import os

from flask import Flask, session,jsonify,abort
from flask_session import Session
from sqlalchemy import create_engine, text
from sqlalchemy.orm import scoped_session, sessionmaker
from flask import render_template,request, url_for, redirect
import requests

app = Flask(__name__)

user = 'postgres'
password = 'Dragonicknight10145!'
host = 'localhost'
port = '5432'
database = 'test'

connection_str = f'postgresql://{user}:{password}@{host}:{port}/{database}'

# Check for environment variable
#if not os.getenv("DATABASE_URL"):
#    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database

engine = create_engine(connection_str)
db = scoped_session(sessionmaker(bind=engine))


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/Register",methods = ["GET","POST"])
def Register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('Password')
        if db.execute(text("SELECT * FROM users WHERE username = :username"),{"username": username}).rowcount !=0:
            message = "that name already exists"
            return render_template("register.html",message=message)



        else:
            db.execute(text("INSERT INTO users (username, passwords) VALUES (:username, :password)"), {"username": username, "password": password })   
            db.commit()
            return render_template("register.html", username=username)
    else:
        return render_template("register.html")
    

@app.route("/login",methods = ["GET","POST"])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('Password')
        finduser = text("SELECT * FROM users WHERE username = :username AND passwords = :password")
        credentials = db.execute(finduser,{"username": username, "password": password }).fetchone()

        if credentials == None:
            result = "Try again"
            return render_template("login.html",result=result)
        if credentials[0] == username and credentials[1] == password:
            session.clear()
            session['logged_in'] = True
            session['username'] = username
            return redirect(url_for("account"))
        else:
            result = "Try again"
            return render_template("login.html",result=result)
    else:
        return render_template("login.html")
    
@app.route("/account/",methods = ["GET","POST"])
def account():    
    if session['logged_in'] == True:
        if request.method == "POST":
           isbn = "%"+request.form.get('isbn')+"%"
           title = "%"+request.form.get('title')+"%"
           author = "%"+request.form.get('author')+"%"
           results = db.execute(text("SELECT * FROM books WHERE isbn LIKE :isbn AND title LIKE :title AND author LIKE :author LIMIT 20"), {"isbn": isbn, "title": title, "author": author }).fetchall()
           return render_template("account.html", search=True, results=results)
        else:
            return render_template("account.html",search = True)
    else:
        return render_template("account.html",search=False)



@app.route("/result/<isbn>", methods=["GET", "POST"])
def result(isbn):
    book_result = db.execute(text("SELECT * FROM books WHERE isbn = :isbn"), {"isbn": isbn}).fetchall()
    book_reviews = db.execute(text("SELECT username, rating, comment FROM Reviews JOIN users ON username = user_id JOIN books ON isbn = book_id WHERE books.isbn = :isbn"), {"isbn": isbn}).fetchall()

    # Function to fetch reviews from Google Books API
    def fetch_google_reviews(isbn):
        url = f"https://www.googleapis.com/books/v1/volumes?q=isbn:{isbn}"
        response = requests.get("https://www.googleapis.com/books/v1/volumes", params={"q": f"isbn:{isbn}"})
        data = response.json()
        google_reviews = []

        if 'items' in data:
            volume_info = data['items'][0]['volumeInfo']

            # Check for ISBN-10 and ISBN-13
            isbn_10 = None
            isbn_13 = None
            for identifier in volume_info.get('industryIdentifiers', []):
                if identifier['type'] == 'ISBN_10':
                    isbn_10 = identifier['identifier']
                elif identifier['type'] == 'ISBN_13':
                    isbn_13 = identifier['identifier']

            # Get average rating and rating count
            average_rating = volume_info.get('averageRating', 'Not Available')
            rating_count = volume_info.get('ratingsCount', 'Not Available')

        return average_rating, rating_count

    if request.method == "GET":
        if session.get('logged_in'):
            if db.execute(text("SELECT * FROM books WHERE isbn = :isbn"), {"isbn": isbn}).rowcount != 0:
                message = isbn

                if not book_reviews:
                    reviews = "There are no reviews yet, leave yours now."
                else:
                    reviews = "Reviews:"

                # Fetch Google reviews
                average_rating, rating_count = fetch_google_reviews(isbn)

                return render_template("result.html", search=True, message=message, book_result=book_result, reviews=reviews, book_reviews=book_reviews, average_rating=average_rating, rating_count=rating_count)
            else:
                return render_template("account.html", search=False)
        else:
            message = "Unauthorized!"
            return render_template("result.html", search=False, message=message)

    if request.method == "POST":
        username = session['username']
        comment = request.form.get('comment')
        rating = request.form.get('rating')
        isbn_id = db.execute(text("SELECT * FROM books WHERE isbn = :isbn"), {"isbn": isbn}).fetchone()[0]
        username_id = db.execute(text("SELECT * FROM users WHERE username = :username"), {"username": username}).fetchone()[0]
        if db.execute(text("SELECT * FROM reviews WHERE user_id = :username_id AND book_id = :isbn_id"), {"username_id": username_id, "isbn_id": isbn_id}).rowcount == 0:
            db.execute(text("INSERT INTO reviews (rating, comment, user_id, book_id) VALUES (:rating, :comment, :username_id, :isbn_id)"), {"rating": rating, "comment": comment, "username_id": username_id, "isbn_id": isbn_id })
            db.commit()
            reviews = "Your review has been submitted"
            return render_template("result.html", search=True, reviews=reviews, book_result=book_result)
        else:
            reviews = "You cannot leave (another) review!"
            return render_template("result.html", search=True, reviews=reviews, book_result=book_result)
    else:
        return render_template("account.html")


def logout():
    session['logged_in']=False
    message = "you have been logged out"
    return render_template("login.html", message=message)



@app.route("/api/<isbn>", methods=["GET"])
def api_book_info(isbn):
    # Function to fetch book info from Google Books API
    def fetch_book_info(isbn):
        url = f"https://www.googleapis.com/books/v1/volumes?q=isbn:{isbn}"
        response = requests.get(url)
        data = response.json()

        book_info = {}

        if 'items' in data:
            volume_info = data['items'][0]['volumeInfo']

            # Get title, authors, published date, and industry identifiers
            title = volume_info.get('title', None)
            authors = volume_info.get('authors', None)
            published_date = volume_info.get('publishedDate', None)
            industry_identifiers = volume_info.get('industryIdentifiers', [])

            isbn_10 = None
            isbn_13 = None
            for identifier in industry_identifiers:
                if identifier['type'] == 'ISBN_10':
                    isbn_10 = identifier['identifier']
                elif identifier['type'] == 'ISBN_13':
                    isbn_13 = identifier['identifier']

            # Get average rating and rating count
            average_rating = volume_info.get('averageRating', None)
            rating_count = volume_info.get('ratingsCount', None)

            book_info = {
                "title": title,
                "authors": authors,
                "publishedDate": published_date,
                "ISBN_10": isbn_10,
                "ISBN_13": isbn_13,
                "reviewCount": rating_count,
                "averageRating": average_rating
            }

        return book_info

    # Fetch book info
    book_info = fetch_book_info(isbn)

    if not book_info:
        abort(404, description="Book not found")

    # Return JSON response
    return jsonify(book_info)
