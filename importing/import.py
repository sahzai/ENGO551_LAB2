import csv
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy import text

user = 'postgres'
password = 'Dragonicknight10145!'
host = 'localhost'
port = '5432'
database = 'test'

connection_str = f'postgresql://{user}:{password}@{host}:{port}/{database}'

engine = create_engine(connection_str)
db = scoped_session(sessionmaker(bind=engine))



def main():
    f = open(r"C:\Users\sahil\Documents\ENGO551\LAB1\project1\project1\importing\books.csv")
    reader = csv.reader(f)
   
    for isbn, title, author, year in reader:
        query =  text("INSERT INTO books (isbn, title, author, year) VALUES (:isbn, :title, :author, :year)")
        
        db.execute(query,{'isbn': isbn, 'title': title, 'author': author, 'year': year})
        print(f"Added book with title {title} to table: books.")
    db.commit()

if __name__ == "__main__":
    main()