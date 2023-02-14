from flask_restx import Resource, Namespace

from flask import request

from app.database import db

from models import MovieSchema, Director, Movie, DirectorSchema

directors_ns = Namespace("directors")

director_schema = DirectorSchema()
directors_schema = DirectorSchema(many=True)

movies_schema = MovieSchema(many=True)


@directors_ns.route("/")
class DirectorsView(Resource):
    def get(self):
        """
        возвращает сериализованные данные обо всех режиссерах
        """
        with db.session.begin():
            directors = db.session.query(Director).all()
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


@directors_ns.route("/<int:did>")
class DirectorsView(Resource):
    def get(self, did: int):
        """
        возвращает все фильмы режиссера
        """
        with db.session.begin():
            director_movies = db.session.query(Movie).filter(Movie.director_id == did)
            if not director_movies:
                return "", 404
            return movies_schema.dump(director_movies), 200

    def put(self, did: int):
        """
        обновляет режиссера в таблице Director
        """
        with db.session.begin():
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
        with db.session.begin():
            try:
                director = db.session.query(Director).get(did)

                db.session.delete(director)
                db.session.commit()
                return "", 204

            except:
                return f" Такой записи в базе нет", 404
