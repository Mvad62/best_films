import csv
import sqlite3
from contextlib import closing
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
CSV_PATH = BASE_DIR / "imdb_top_250.csv"
DB_PATH = BASE_DIR / "imdb_top.db"


def create_database(db_path=DB_PATH):
    db_path = Path(db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)

    with closing(sqlite3.connect(db_path)) as connection, connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS films (
                rank INTEGER PRIMARY KEY,
                title TEXT NOT NULL,
                year INTEGER,
                genre TEXT,
                duration TEXT,
                origin TEXT,
                director TEXT,
                imdb_rating REAL,
                rating_count INTEGER,
                imdb_link TEXT
            )
            """
        )


def import_csv(csv_path=CSV_PATH, db_path=DB_PATH):
    csv_path = Path(csv_path)
    db_path = Path(db_path)
    create_database(db_path)

    with csv_path.open("r", encoding="utf-8-sig", newline="") as csv_file:
        reader = csv.DictReader(csv_file)
        films = [
            (
                int(row[""]),
                row["Title"],
                int(row["Year"]),
                row["Genre"],
                row["Duration"],
                row["Origin"],
                row["Director"],
                float(row["IMDB rating"]),
                int(row["Rating count"]),
                row["IMDB link"],
            )
            for row in reader
        ]

    with closing(sqlite3.connect(db_path)) as connection, connection:
        connection.execute("DELETE FROM films")
        connection.executemany(
            """
            INSERT INTO films (
                rank, title, year, genre, duration, origin, director,
                imdb_rating, rating_count, imdb_link
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            films,
        )

    return len(films)


if __name__ == "__main__":
    imported_count = import_csv()
    print(f"Imported {imported_count} films into {DB_PATH}")