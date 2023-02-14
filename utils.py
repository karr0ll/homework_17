from flask import request
from sqlalchemy import func

from app.database import db

from models import Genre, Director

#from app import application

# additional functions
#with application.app_context():
def check_and_add_genres():
    """
    проверяет наличие жанра в таблице
    добавляет новый жанр, если его нет в таблицe
    """
    request_json = request.json
    all_genres = db.session.query(Genre).all()
    genre = request_json.get("genre")

    all_genres_response = []
    for item in all_genres:
        all_genres_response.append(item.name)

    if genre not in all_genres_response:
        genre_id = db.session.query(Genre, func.max(Genre.id)).one()
        new_genre = Genre(
            id=genre_id[1] + 1,
            name=genre
        )

        db.session.add(new_genre)
        db.session.commit()


def check_and_add_directors():
    """
    проверяет наличие режиссера в таблице
    добавляет нового режиссера, если его нет в таблицу
    """
    request_json = request.json
    all_genres = db.session.query(Director).all()
    director = request_json.get("director")

    all_directors_response = []
    for item in all_genres:
        all_directors_response.append(item.name)

    if director not in all_directors_response:
        director_id = db.session.query(Director, func.max(Director.id)).one()
        new_director = Director(
            id=director_id[1] + 1,
            name=director
        )

        db.session.add(new_director)
        db.session.commit()


def set_genre_id(genre_name):
    """
    получает номер последнего id в таблице genre
    (в таблице нет autoincrement PK)
    """
    all_genres = db.session.query(Genre).all()
    for genre in all_genres:
        if genre_name == genre.name:
            genre_id = genre.id
            return genre_id


def set_director_id(director_name):
    """
    получает номер последнего id в таблице director
    (в таблице нет autoincrement PK)
    """
    all_directors = db.session.query(Director).all()
    for director in all_directors:
        if director_name == director.name:
            director_id = director.id
            return director_id

