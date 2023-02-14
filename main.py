from flask import Flask
from flask_restx import Api

from app.data import data
from app.config import Config
from app.database import db
from views.directors import directors_ns
from views.genres import genres_ns
from views.movies import movies_ns
from models import Movie, Director, Genre


def create_app(config: Config):
    application = Flask(__name__)  # инициализация(создание) приложения
    application.config.from_object(config)  # конфигурирование приложения
    application.app_context().push() # создание app_context для приложения чтобы можно было работать с бд
    return application


def configure_app(application: Flask):  # конфигурирование приложения
    db.init_app(application)  # подключение БД

    api = Api(application)  # создание API
    api.add_namespace(directors_ns)  # добавление namespace
    api.add_namespace(genres_ns)
    api.add_namespace(movies_ns)


def create_data():
    with db.session.begin():
        db.drop_all()
        db.create_all()

        for movie in data["movies"]:
            m = Movie(
                id=movie["pk"],
                title=movie["title"],
                description=movie["description"],
                trailer=movie["trailer"],
                year=movie["year"],
                rating=movie["rating"],
                genre_id=movie["genre_id"],
                director_id=movie["director_id"],
            )
            db.session.add(m)

        for director in data["directors"]:
            d = Director(
                id=director["pk"],
                name=director["name"],
            )
            db.session.add(d)

        for genre in data["genres"]:
            d = Genre(
                id=genre["pk"],
                name=genre["name"],
            )
            db.session.add(d)


if __name__ == '__main__':
    app_config = Config()  # загрузка конфига
    app = create_app(app_config)  # создание приложения

    configure_app(app)  # конфигурирование приложения
    create_data()  # загрузка данных и создание БД
    app.run()  # запуск приложения
