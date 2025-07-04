import pandas as pd
import psycopg2

# Database connection parameters — update these
conn = psycopg2.connect(
    dbname="movielens100k",
    user="postgres",       # e.g., "postgres"
    password="siddhesh",   # e.g., "admin" or your DB password
    host="localhost",
    port="5432"
)
cur = conn.cursor()

# 1. Load Users
users = pd.read_csv(
    "ml-100k/u.user", sep="|",
    names=["user_id", "age", "gender", "occupation", "zip_code"]
)
for row in users.itertuples(index=False):
    cur.execute(
        "INSERT INTO users (user_id, age, gender, occupation, zip_code) VALUES (%s, %s, %s, %s, %s)",
        (row.user_id, row.age, row.gender, row.occupation, row.zip_code)
)

# 2. Load Movies
# Only using movie_id, title, and genres (concatenated for simplicity)
movies = pd.read_csv(
    "ml-100k/u.item", sep="|", encoding="latin-1", header=None,
    usecols=[0, 1] + list(range(5, 24)),
)
genre_cols = [
    "unknown", "Action", "Adventure", "Animation", "Children's", "Comedy", "Crime",
    "Documentary", "Drama", "Fantasy", "Film-Noir", "Horror", "Musical",
    "Mystery", "Romance", "Sci-Fi", "Thriller", "War", "Western"
]
movies.columns = ["movie_id", "title"] + genre_cols
movies["genre"] = movies[genre_cols].apply(lambda x: ", ".join(x.index[x == 1]), axis=1)
movies = movies[["movie_id", "title", "genre"]]

for row in movies.itertuples(index=False):
    cur.execute(
        "INSERT INTO movies (movie_id, title, genre) VALUES (%s, %s, %s)",
        (row.movie_id, row.title, row.genre)
)

# 3. Load Ratings
ratings = pd.read_csv(
    "ml-100k/u.data", sep="\t",
    names=["user_id", "movie_id", "rating", "timestamp"]
)
for row in ratings.itertuples(index=False):
    cur.execute(
        "INSERT INTO ratings (user_id, movie_id, rating, timestamp) VALUES (%s, %s, %s, %s)",
        (row.user_id, row.movie_id, row.rating, row.timestamp)
)

conn.commit()
cur.close()
conn.close()
print("✅ Data successfully loaded into PostgreSQL.")
