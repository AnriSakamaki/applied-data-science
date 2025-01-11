import sqlite3

# DB SETUP
conn = sqlite3.connect('movies.db')
cursor = conn.cursor()

def insert_actor_into_actors_table(actor_name, actor_bio, actor_link):
    sql = f'SELECT MAX(actor_id) FROM actors'
    cursor.execute(sql)
    result = cursor.fetchone()
    if result[0] is None:
        actor_id = 0
    else:
        actor_id = result[0] + 1
    sql = f'INSERT INTO actors (actor_id, actor_name, actor_bio, actor_link) VALUES (?, ?, ?, ?)'
    cursor.execute(sql, (actor_id, actor_name, actor_bio, actor_link))
    conn.commit()
    return actor_id

def insert_award_into_awards_table(actor_id, award_name, award_category, award_year):
    sql = f'SELECT MAX(awards_id) FROM awards'
    cursor.execute(sql)
    result = cursor.fetchone()
    if result[0] is None:
        awards_id = 0
    else:
        awards_id = result[0] + 1
    sql = f'INSERT INTO awards (awards_id, actor_id, award_name, award_category, award_year) VALUES (?, ?, ?, ?, ?)'
    cursor.execute(sql, (awards_id, actor_id, award_name, award_category, award_year))
    conn.commit()

def insert_movie_into_movies_table(movie_name, movie_rating, movie_year, movie_genres, movie_url):
    sql = f'SELECT MAX(movie_id) FROM movies'
    cursor.execute(sql)
    result = cursor.fetchone()
    if result[0] is None:
        movie_id = 0
    else:
        movie_id = result[0] + 1
    sql = f'INSERT INTO movies (movie_id, movie_name, movie_rating, movie_year, movie_genres, movie_url) VALUES (?, ?, ?, ?, ?, ?)'
    cursor.execute(sql, (movie_id, movie_name, movie_rating, movie_year, movie_genres, movie_url))
    conn.commit()
    return movie_id

def insert_entry_in_played_in_table(actor_id, movie_id):
    sql = f'INSERT INTO played_in (actor_id, movie_id) VALUES (?, ?)'
    cursor.execute(sql, (actor_id, movie_id))
    conn.commit()

def insert_into_actor_movie_staging_table(actor_id, movie_name, movie_url):
    sql = f'INSERT INTO actor_movie_staging (actor_id, movie_name, movie_url) VALUES (?, ?, ?)'
    cursor.execute(sql, (actor_id, movie_name, movie_url))
    conn.commit()

def get_all_actors():
    sql = f'SELECT actor_id, actor_name FROM actors'
    cursor.execute(sql)
    result = cursor.fetchall()
    conn.commit()
    return result

def get_all_movies():
    sql = f'SELECT movie_id, movie_name, movie_url FROM movies'
    cursor.execute(sql)
    result = cursor.fetchall()
    conn.commit()
    return result

def get_movie_id(movie_url):
    sql = f'SELECT movie_id FROM movies WHERE movie_url = ?'
    cursor.execute(sql, (movie_url, ))
    result = cursor.fetchone()
    conn.commit()
    return result

def get_actor_bio(actor_id):
    sql = f'SELECT actor_bio FROM actors WHERE actor_id = ?'
    cursor.execute(sql, (actor_id,))
    result = cursor.fetchone()
    conn.commit()
    return result

def get_actor_links():
    sql = f'SELECT actor_id, actor_name, actor_link FROM actors'
    cursor.execute(sql)
    result = cursor.fetchall()
    conn.commit()
    return result

def get_actor_movies(actor_id):
    sql = f'SELECT * FROM played_in INNER JOIN movies USING (movie_id) WHERE actor_id = ?'
    cursor.execute(sql, (actor_id, ))
    result = cursor.fetchall()
    conn.commit()
    return result

def get_actor_awards(actor_id):
    sql = f'SELECT * FROM awards WHERE actor_id = ?'
    cursor.execute(sql, (actor_id, ))
    result = cursor.fetchall()
    conn.commit()
    return result

def get_actors_in_awards():
    sql = f'SELECT DISTINCT actor_name FROM awards INNER JOIN actors USING(actor_id)'
    cursor.execute(sql)
    result = cursor.fetchall()
    conn.commit()
    return result

def get_actors_in_actor_movie_staging():
    sql = f'SELECT DISTINCT actor_name FROM actor_movie_staging INNER JOIN actors USING(actor_id)'
    cursor.execute(sql)
    result = cursor.fetchall()
    conn.commit()
    return result

def get_actor_genres(actor_id):
    sql = f'SELECT movie_genres FROM movies INNER JOIN played_in USING (movie_id) WHERE actor_id = ?'
    cursor.execute(sql, (actor_id, ))
    result = cursor.fetchall()
    conn.commit()
    return result

def get_actor_movies_average_rating(actor_id):
    sql = f'SELECT AVG(movie_rating) FROM movies INNER JOIN played_in USING (movie_id) WHERE actor_id = ?'
    cursor.execute(sql, (actor_id, ))
    result = cursor.fetchone()
    conn.commit()
    return result

def get_actor_top_five_movies(actor_id):
    sql = f'SELECT * FROM movies INNER JOIN played_in USING(movie_id) WHERE actor_id = ? ORDER BY movie_rating DESC LIMIT 5'
    cursor.execute(sql, (actor_id, ))
    result = cursor.fetchall()
    conn.commit()
    return result

def get_all_actor_movie_staging_table():
    sql = f'SELECT * FROM actor_movie_staging'
    cursor.execute(sql)
    result = cursor.fetchall()
    conn.commit()
    return result

def reset_database():
    sql = '''DROP TABLE IF EXISTS "actors";'''
    cursor.execute(sql)
    sql = '''CREATE TABLE "actors" (
        "actor_id"	INTEGER NOT NULL UNIQUE,
        "actor_name"	TEXT NOT NULL,
        "actor_bio"	TEXT,
        "actor_link" TEXT,
        PRIMARY KEY("actor_id")
    );'''
    cursor.execute(sql)

    sql = '''DROP TABLE IF EXISTS "awards";'''
    cursor.execute(sql)
    sql = '''CREATE TABLE "awards" (
        "awards_id" INTEGER NOT NULL UNIQUE,
        "actor_id"	INTEGER NOT NULL,
        "award_name"	TEXT NOT NULL,
        "award_category"	TEXT,
        "award_year"	INTEGER NOT NULL,
        PRIMARY KEY("awards_id")
    );'''
    cursor.execute(sql)

    sql = '''DROP TABLE IF EXISTS "movies";'''
    cursor.execute(sql)
    sql = ''' CREATE TABLE "movies" (
        "movie_id"	INTEGER NOT NULL UNIQUE,
        "movie_name"	TEXT NOT NULL,
        "movie_rating"	TEXT,
        "movie_year"	INTEGER,
        "movie_genres"	TEXT,
        "movie_url" TEXT,
        PRIMARY KEY("movie_id")
    );'''
    cursor.execute(sql)

    sql = '''DROP TABLE IF EXISTS "played_in";'''
    cursor.execute(sql)
    sql = ''' CREATE TABLE "played_in" (
        "actor_id"	INTEGER NOT NULL,
        "movie_id"	INTEGER NOT NULL,
        PRIMARY KEY("actor_id","movie_id")
    );'''
    cursor.execute(sql)

    sql = ''' DROP TABLE IF EXISTS "actor_movie_staging";'''
    cursor.execute(sql)
    sql = ''' CREATE TABLE "actor_movie_staging" (
        "actor_id"	INTEGER NOT NULL,
        "movie_name"	TEXT NOT NULL,
        "movie_url"	TEXT NOT NULL,
        PRIMARY KEY("actor_id","movie_name","movie_url")
    );'''
    cursor.execute(sql)

    conn.commit()

if __name__ == '__main__':
    reset_database()

    conn.commit()
    conn.close()