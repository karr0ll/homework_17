from flask_restx import Resource, Namespace

from flask import request

from app.database import db

from models import Movie, Genre, MovieSchema, GenreSchema

genres_ns = Namespace("genres")

genre_schema = GenreSchema()
genres_schema = GenreSchema(many=True)
movies_schema = MovieSchema(many=True)



@genres_ns.route("/")
class GenresView(Resource):
    def get(self):
        """
        возвращает все жанры
        """
        with db.session.begin():
            genres = db.session.query(Genre).all()
            if not genres:
                return "", 404
            return genres_schema.dump(genres), 200

    def post(self):
        """
        добавляет новый жанр в таблицу Genre
        """
        request_json = request.json
        new_genre = Genre(**request_json)

        with db.session.begin():
            db.session.add(new_genre)
            db.session.commit()  # commit added

        return "", 201


@genres_ns.route("/<int:gid>")
class GenresView(Resource):
    def get(self, gid: int):
        """
        возвращает все фильмы жанра
        """
        with db.session.begin():
            all_movies_by_genre = db.session.query(Movie).filter(Movie.genre_id == gid)
            return movies_schema.dump(all_movies_by_genre)

    def put(self, gid: int):
        """
        обновляет жанр в таблице Genre
        """
        with db.session.begin():
            genre = db.session.query(Genre).get(gid)
            request_json = request.json

            genre.id = request_json.get("id")
            genre.name = request_json.get("name")
            db.session.add(genre)
            db.session.commit()

            return "", 200

    def delete(self, gid: int):
        """
        удаляет жанр в таблице Genre
        """
        with db.session.begin():
            try:
                genre = db.session.query(Genre).get(gid)

                db.session.delete(genre)
                db.session.commit()
                return "", 204

            except:
                return "Такой записи в базе нет", 404
