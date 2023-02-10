from flask import Flask, request
from flask_restx import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


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

genre_schema = DirectorSchema()

api = Api(app)
movies_ns = api.namespace("movies")
directors_ns = api.namespace("directors")
genres_ns = api.namespace("genres")


@movies_ns.route("/")
class MoviesView(Resource):
    def get(self):
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
            paginated_movies = db.session.query(Movie).order_by(Movie.id)[pagination_from:pagination_to]
            return movies_schema.dump(paginated_movies), 200


@movies_ns.route("/<int:mid>")
class MoviesView(Resource):
    def get(self, mid: int):
        movie = db.session.query(Movie).get(mid)
        return movie_schema.dump(movie), 200


@directors_ns.route("/")
class DirectorsView(Resource):
    def post(self):
        request_json = request.json
        new_director = Director(**request_json)

        with db.session.begin():
            db.session.add(new_director)

        return "", 201


@directors_ns.route("/<int:did>")
class DirectorsView(Resource):
    def put(self, did: int):
        director = db.session.query(Director).get(did)
        request_json = request.json

        director.id = request_json.get("id")
        director.name = request_json.get("name")
        db.session.add(director)
        db.session.commit()

        return "", 200

    def delete(self, did: int):
        try:
            director = db.session.query(Director).get(did)

            db.session.delete(director)
            db.session.commit()
            return "", 204

        except:
            return f" Такой записи в базе нет", 404


@genres_ns.route("/")
class GenresView(Resource):
    def post(self):
        request_json = request.json
        new_genre = Genre(**request_json)

        with db.session.begin():
            db.session.add(new_genre)

        return "", 201


@genres_ns.route("/<int:gid>")
class GenresView(Resource):
    def put(self, gid: int):
        genre = db.session.query(Genre).get(gid)
        request_json = request.json

        genre.id = request_json.get("id")
        genre.name = request_json.get("name")
        db.session.add(genre)
        db.session.commit()

        return "", 200

    def delete(self, gid: int):
        try:
            genre = db.session.query(Genre).get(gid)

            db.session.delete(genre)
            db.session.commit()
            return "", 204

        except:
            return "Такой записи в базе нет", 404


if __name__ == '__main__':
    app.run(debug=True)
