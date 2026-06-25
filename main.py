import uuid
import random
from datetime import datetime, timedelta

import psycopg2
from psycopg2.extras import execute_values
from faker import Faker


# Connection settings
HOST = 'localhost' # put your credentials here
USER = 'postgres' # put your credentials here
PASSWORD = 'my_password1' # put your credentials here
DATABASE = 'music_platform' # put your credentials here
PORT = '5432' # put your credentials here

# Data volume settings
USERS_COUNT = 100_000
SONGS_COUNT = 10_000
PLAYLISTS_ROW_COUNT = 1_000_000
CHUNK_SIZE = 10_000

fake = Faker()


def insert_users(cursor):
    print("Inserting into users...")

    user_insert_query = """
        INSERT INTO users
            (user_id, user_first_name, user_last_name, email, phone, subscription_type)
        VALUES %s
    """

    user_ids = []

    for start in range(0, USERS_COUNT, CHUNK_SIZE):
        current_chunk_size = min(CHUNK_SIZE, USERS_COUNT - start)

        users_data = []
        for _ in range(current_chunk_size):
            user_id = str(uuid.uuid4())
            user_ids.append(user_id)

            users_data.append(
                (
                    user_id,
                    fake.first_name(),
                    fake.last_name(),
                    fake.email(),
                    fake.phone_number(),
                    random.choice(["free", "premium"]),
                )
            )

        execute_values(cursor, user_insert_query, users_data)
        print(f"Inserted {start + current_chunk_size} rows into ousers...")

    print("Inserted into opt_clients.")
    return user_ids


def insert_songs(cursor):
    print("Inserting into music...")

    song_insert_query = """
        INSERT INTO music
            (song_title, genre, description)
        VALUES %s
        RETURNING song_id
    """

    genres = ["Pop", "Rock", "Hip-hop", "Jazz", "Classical music"]

    songs_data = [
        (
            fake.word(),
            random.choice(genres),
            fake.text(),
        )
        for _ in range(SONGS_COUNT)
    ]

    execute_values(cursor, song_insert_query, songs_data)

    song_ids = [row[0] for row in cursor.fetchall()]

    print("Inserted into music.")
    return song_ids


def insert_playlists(cursor, user_ids, song_ids):
    print("Inserting into playlists...")

    playlist_insert_query = """
        INSERT INTO playlists
            (added_date, user_id, song_id)
        VALUES %s
    """

    added_date_start = datetime.now() - timedelta(days=365 * 5)

    for start in range(0, PLAYLISTS_ROW_COUNT, CHUNK_SIZE):
        current_chunk_size = min(CHUNK_SIZE, PLAYLISTS_ROW_COUNT - start)

        playlist_data = [
            (
                added_date_start + timedelta(days=random.randint(0, 365 * 5)),
                random.choice(user_ids),
                random.choice(song_ids),
            )
            for _ in range(current_chunk_size)
        ]

        execute_values(cursor, playlist_insert_query, playlist_data)
        print(f"Inserted {start + current_chunk_size} rows into playlists...")

    print("Inserted into playlists.")


def main():
    connection = psycopg2.connect(
        host=HOST,
        user=USER,
        password=PASSWORD,
        dbname=DATABASE,
        port=PORT,
    )

    try:
        with connection:
            with connection.cursor() as cursor:
                user_ids = insert_users(cursor)
                song_ids = insert_songs(cursor)
                insert_playlists(cursor, user_ids, song_ids)

    finally:
        connection.close()


if __name__ == "__main__":
    main()
