from flask_restx import Resource, Namespace

from flask import request

from app.database import db

from models import Movie, MovieSchema
from utils import check_and_add_genres, check_and_add_directors, set_genre_id, set_director_id

movies_ns = Namespace("movies")

movie_schema = MovieSchema()
movies_schema = MovieSchema(many=True)

@movies_ns.route("/")
class MoviesView(Resource):
    def get(self):
        """
        возвращает сериализованные данные о фильмах
        """
        with db.session.begin():
            director_id = request.args.get("director_id")
            genre_id = request.args.get("genre_id")

            page = int(request.args.get("page", 1))
            movies_per_page = 5

            pagination_from = (page - 1) * movies_per_page
            pagination_to = page * movies_per_page

            if director_id:
                movies_by_director = db.session.query(Movie).filter(Movie.director_id == director_id)
                if len(movies_schema.dump(movies_by_director)) > 0:
                    return movies_schema.dump(movies_by_director), 200
                else:
                    return "", 204

            if genre_id:
                movies_by_genre = db.session.query(Movie).filter(Movie.genre_id == genre_id)
                if len(movies_schema.dump(movies_by_genre)) > 0:
                    return movies_schema.dump(movies_by_genre), 200
                else:
                    return "", 204

            else:
                paginated_movies = Movie.query.order_by(Movie.id)[pagination_from:pagination_to]
                return movies_schema.dump(paginated_movies), 200

    def post(self):
        """
        добавляет новый фильм в таблицу Movie
        """
        with db.session.begin():

            request_json = request.json

            check_and_add_genres()
            check_and_add_directors()

            new_movie = Movie(
                id=request_json.get("id"),
                title=request_json.get("title"),
                description=request_json.get("description"),
                trailer=request_json.get("trailer"),
                year=request_json.get("year"),
                rating=request_json.get("rating"),
                genre_id=set_genre_id(request_json.get("genre")),
                director_id=set_director_id(request_json.get("director"))
            )
            db.session.add(new_movie)
            db.session.commit()

            return "", 201


@movies_ns.route("/<int:mid>")
class MoviesView(Resource):
    def get(self, mid: int):
        """
        возвращает сериализованные данные об одном фильме
        """
        with db.session.begin():
            movie = db.session.query(Movie).get(mid)
            if not movie:
                return "", 404
            return movie_schema.dump(movie), 200

    def put(self, mid: int):
        with db.session.begin():
            movie = db.session.query(Movie).get(mid)
            request_json = request.json

            check_and_add_genres()
            check_and_add_directors()

            movie.id = request_json.get("id")
            movie.title = request_json.get("title")
            movie.description = request_json.get("description")
            movie.trailer = request_json.get("trailer")
            movie.year = request_json.get("year")
            movie.rating = request_json.get("rating")
            movie.genre_id = set_genre_id(request_json.get("genre"))
            movie.director_id = set_director_id(request_json.get("director"))

            db.session.add(movie)
            db.session.commit()

            return "", 200

    def delete(self, mid: int):
        with db.session.begin():
            try:
                movie = db.session.query(Movie).get(mid)
                db.session.delete(movie)
                db.session.commit()
            except:
                return f" Такой записи в базе нет", 404

