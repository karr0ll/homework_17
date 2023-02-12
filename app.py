from flask import Flask, request
from flask_restx import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields
from sqlalchemy import func

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# db models

class Movie(db.Model):
    __tablename__ = 'movie'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    description = db.Column(db.String(255))
    trailer = db.Column(db.String(255))
    year = db.Column(db.Integer)
    rating = db.Column(db.Float)
    genre_id = db.Column(db.Integer, db.ForeignKey("genre.id"))
    genre = db.relationship("Genre")
    director_id = db.Column(db.Integer, db.ForeignKey("director.id"))
    director = db.relationship("Director")


class Director(db.Model):
    __tablename__ = 'director'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


class Genre(db.Model):
    __tablename__ = 'genre'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


# schemas

class DirectorSchema(Schema):
    id = fields.Int()
    name = fields.Str()


class GenreSchema(Schema):
    id = fields.Int()
    name = fields.Str()


class MovieSchema(Schema):
    id = fields.Int()
    title = fields.Str()
    description = fields.Str()
    trailer = fields.Str()
    year = fields.Int()
    rating = fields.Float()
    genre = fields.Pluck(GenreSchema, "name")
    director = fields.Pluck(DirectorSchema, "name")


movie_schema = MovieSchema()
movies_schema = MovieSchema(many=True)

director_schema = DirectorSchema()
directors_schema = DirectorSchema(many=True)

genre_schema = GenreSchema()
genres_schema = GenreSchema(many=True)

# namespaces

api = Api(app)
movies_ns = api.namespace("movies")
directors_ns = api.namespace("directors")
genres_ns = api.namespace("genres")

# additional functions
with app.app_context():
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


# Movie http methods

@movies_ns.route("/")
class MoviesView(Resource):
    def get(self):
        """
        возвращает сериализованные данные о фильмах
        """
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
        db.session.close()

        return "", 201


@movies_ns.route("/<int:mid>")
class MoviesView(Resource):
    def get(self, mid: int):
        """
        возвращает сериализованные данные об одном фильме
        """
        movie = db.session.query(Movie).get(mid)
        if not movie:
            return "", 404
        return movie_schema.dump(movie), 200

    def put(self, mid: int):
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

        try:
            movie = db.session.query(Movie).get(mid)
            db.session.delete(movie)
            db.session.commit()
        except:
            return f" Такой записи в базе нет", 404


@directors_ns.route("/")
class DirectorsView(Resource):
    def get(self):
        """
        возвращает сериализованные данные обо всех режиссерах
        """
        directors = db.session.query(Director).get(all)
        if not directors:
            return "", 404
        return directors_schema.dump(directors), 200

    def post(self):
        """
        добавляет нового режиссера в таблицу Director
        """
        request_json = request.json
        new_director = Director(**request_json)

        with db.session.begin():
            db.session.add(new_director)
            db.session.commit()  # commit added

        return "", 201


# Director http methods

@directors_ns.route("/<int:did>")
class DirectorsView(Resource):
    def get(self, did: int):
        """
        возвращает все фильмы режиссера
        """

        director_movies = db.session.query(Movie).filter(Movie.director_id == did)
        if not director_movies:
            return "", 404
        return movies_schema.dump(director_movies), 200

    def put(self, did: int):
        """
        обновляет режиссера в таблице Director
        """
        director = db.session.query(Director).get(did)
        request_json = request.json

        director.id = request_json.get("id")
        director.name = request_json.get("name")
        db.session.add(director)
        db.session.commit()

        return "", 200

    def delete(self, did: int):
        """
        удаляет режиссера в таблице Director
        """
        try:
            director = db.session.query(Director).get(did)

            db.session.delete(director)
            db.session.commit()
            return "", 204

        except:
            return f" Такой записи в базе нет", 404


# Genre http methods
@genres_ns.route("/")
class GenresView(Resource):
    def get(self):
        """
        возвращает все жанры
        """
        all_genres = db.session.query(Genre).all()
        return genres_schema.dump(all_genres)

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
        all_movies = db.session.query(Movie).filter(Movie.genre_id == gid)
        return movies_schema.dump(all_movies)

    def put(self, gid: int):
        """
        обновляет жанр в таблице Genre
        """
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
        try:
            genre = db.session.query(Genre).get(gid)

            db.session.delete(genre)
            db.session.commit()
            return "", 204

        except:
            return "Такой записи в базе нет", 404


if __name__ == '__main__':
    app.run(debug=True)
