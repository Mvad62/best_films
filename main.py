import sqlite3
from contextlib import closing

from database import DB_PATH, create_database
from database_manager import create_film, search_by_genre, search_by_title


def _read_int(prompt):
    while True:
        try:
            return int(input(prompt).strip())
        except ValueError:
            print("Введите целое число.")


def _read_optional_int(prompt):
    while True:
        value = input(prompt).strip()
        if not value:
            return None
        try:
            return int(value)
        except ValueError:
            print("Введите целое число или оставьте поле пустым.")


def _read_optional_float(prompt):
    while True:
        value = input(prompt).strip().replace(",", ".")
        if not value:
            return None
        try:
            return float(value)
        except ValueError:
            print("Введите число или оставьте поле пустым.")


def _print_films(films):
    if not films:
        print("Фильмы не найдены.")
        return

    for film in films:
        print(
            f"#{film['rank']} | {film['title']} ({film['year']}) | "
            f"{film['genre']} | рейтинг: {film['imdb_rating']}"
        )


def search_movies_by_genre():
    genre = input("Введите жанр для поиска: ").strip()
    _print_films(search_by_genre(genre))


def search_movies_by_title():
    word = input("Введите слово или часть названия: ").strip()
    _print_films(search_by_title(word))


def delete_films_older_than_year():
    year = _read_int("Удалить фильмы, выпущенные раньше какого года? ")
    create_database(DB_PATH)

    with closing(sqlite3.connect(DB_PATH)) as connection, connection:
        count = connection.execute(
            "SELECT COUNT(*) FROM films WHERE year < ?", (year,)
        ).fetchone()[0]

    if count == 0:
        print("Фильмы до указанного года не найдены.")
        return

    confirmation = input(
        f"Будет удалено фильмов: {count}. Подтвердить? (да/нет): "
    ).strip().casefold()
    if confirmation != "да":
        print("Удаление отменено.")
        return

    with closing(sqlite3.connect(DB_PATH)) as connection, connection:
        cursor = connection.execute("DELETE FROM films WHERE year < ?", (year,))

    print(f"Удалено фильмов: {cursor.rowcount}.")


def add_new_film():
    title = input("Название фильма: ").strip()
    while not title:
        print("Название не может быть пустым.")
        title = input("Название фильма: ").strip()

    year = _read_optional_int("Год выпуска: ")
    genre = input("Жанр: ").strip() or None
    duration = input("Продолжительность: ").strip() or None
    origin = input("Страна: ").strip() or None
    director = input("Режиссер: ").strip() or None
    imdb_rating = _read_optional_float("Рейтинг IMDb: ")
    rating_count = _read_optional_int("Количество оценок: ")
    imdb_link = input("Ссылка IMDb: ").strip() or None

    rank = create_film(
        title=title,
        year=year,
        genre=genre,
        duration=duration,
        origin=origin,
        director=director,
        imdb_rating=imdb_rating,
        rating_count=rating_count,
        imdb_link=imdb_link,
    )
    print(f"Фильм добавлен под номером {rank}.")


def show_film_count():
    create_database(DB_PATH)
    with closing(sqlite3.connect(DB_PATH)) as connection, connection:
        count = connection.execute("SELECT COUNT(*) FROM films").fetchone()[0]
    print(f"Количество фильмов в базе: {count}.")


def show_top_5_films():
    create_database(DB_PATH)
    with closing(sqlite3.connect(DB_PATH)) as connection, connection:
        connection.row_factory = sqlite3.Row
        films = connection.execute(
            """
            SELECT rank, title, year, imdb_rating
            FROM films
            WHERE imdb_rating IS NOT NULL
            ORDER BY imdb_rating DESC, rating_count DESC, rank ASC
            LIMIT 5
            """
        ).fetchall()

    if not films:
        print("В базе пока нет фильмов с рейтингом.")
        return

    print("Топ-5 фильмов по рейтингу IMDb:")
    for position, film in enumerate(films, start=1):
        print(
            f"{position}. {film['title']} ({film['year']}) "
            f"- {film['imdb_rating']}"
        )


def main():
    actions = {
        "1": search_movies_by_genre,
        "2": delete_films_older_than_year,
        "3": add_new_film,
        "4": show_film_count,
        "5": show_top_5_films,
        "6": search_movies_by_title,
    }

    while True:
        print(
            "\nВыберите действие:\n"
            "1. Поиск фильмов по жанру\n"
            "2. Удалить фильмы старше года\n"
            "3. Добавить новый фильм\n"
            "4. Показать количество фильмов в базе\n"
            "5. Топ-5 фильмов по рейтингу\n"
            "6. Поиск фильма по слову в названии\n"
            "0. Выход"
        )
        choice = input("> ").strip()

        if choice == "0":
            print("До свидания.")
            break

        action = actions.get(choice)
        if action is None:
            print("Неизвестная команда. Выберите пункт от 0 до 6.")
            continue

        action()


if __name__ == "__main__":
    main()