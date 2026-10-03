import sqlite3
from contextlib import closing

from database import DB_PATH, create_database


EDITABLE_FIELDS = {
    "title",
    "year",
    "genre",
    "duration",
    "origin",
    "director",
    "imdb_rating",
    "rating_count",
    "imdb_link",
}


def _connect(db_path):
    create_database(db_path)
    return sqlite3.connect(db_path)


def create_film(
    title,
    year=None,
    genre=None,
    duration=None,
    origin=None,
    director=None,
    imdb_rating=None,
    rating_count=None,
    imdb_link=None,
    db_path=DB_PATH,
):
    with closing(_connect(db_path)) as connection, connection:
        next_rank = connection.execute(
            "SELECT COALESCE(MAX(rank), 0) + 1 FROM films"
        ).fetchone()[0]
        connection.execute(
            """
            INSERT INTO films (
                rank, title, year, genre, duration, origin, director,
                imdb_rating, rating_count, imdb_link
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                next_rank,
                title,
                year,
                genre,
                duration,
                origin,
                director,
                imdb_rating,
                rating_count,
                imdb_link,
            ),
        )

    return next_rank


def edit_film(rank, db_path=DB_PATH, **fields):
    if not fields:
        raise ValueError("Укажите хотя бы одно поле для изменения")

    invalid_fields = fields.keys() - EDITABLE_FIELDS
    if invalid_fields:
        raise ValueError(f"Недопустимые поля: {', '.join(sorted(invalid_fields))}")

    assignments = ", ".join(f"{field} = ?" for field in fields)
    values = [*fields.values(), rank]
    with closing(_connect(db_path)) as connection, connection:
        cursor = connection.execute(
            f"UPDATE films SET {assignments} WHERE rank = ?", values
        )

    return cursor.rowcount > 0


def delete_film(rank, db_path=DB_PATH):
    with closing(_connect(db_path)) as connection, connection:
        cursor = connection.execute("DELETE FROM films WHERE rank = ?", (rank,))

    return cursor.rowcount > 0


def search_by_genre(genre, db_path=DB_PATH):
    if not genre.strip():
        return []

    with closing(_connect(db_path)) as connection, connection:
        connection.row_factory = sqlite3.Row
        films = connection.execute(
            "SELECT * FROM films WHERE genre LIKE ? ORDER BY rank",
            (f"%{genre}%",),
        ).fetchall()

    return [dict(film) for film in films]


def search_by_title(word, db_path=DB_PATH):
    if not word.strip():
        return []

    with closing(_connect(db_path)) as connection, connection:
        connection.row_factory = sqlite3.Row
        films = connection.execute(
            "SELECT * FROM films WHERE title LIKE ? ORDER BY rank",
            (f"%{word}%",),
        ).fetchall()

    return [dict(film) for film in films]