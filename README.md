# Project 1

ENGO 551

Postgres databse construction was done in PGADMIN

Bookreview website will work as shown in submitted screencast

This iteration of the project involves using the google books api to fetch an average rating and review count for each isbn, this is done on each bookpage
this iteration also includes a /api/<isbn> route that will return a json of the following format

book_info = {
                "title": title,
                "authors": authors,
                "publishedDate": published_date,
                "ISBN_10": isbn_10,
                "ISBN_13": isbn_13,
                "reviewCount": rating_count,
                "averageRating": average_rating
            }

