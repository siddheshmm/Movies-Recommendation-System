import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from psycopg2 import connect

# Connect to database
conn = connect(
    dbname="movielens100k",
    user="postgres",
    password="siddhesh",
    host="localhost",
    port="5432"
)

# Load data
ratings = pd.read_sql("SELECT * FROM ratings", conn)
movies = pd.read_sql("SELECT * FROM movies", conn)

# Create user-item matrix
user_item_matrix = ratings.pivot(index="user_id", columns="movie_id", values="rating").fillna(0)

# Compute user-user similarity
user_similarity = cosine_similarity(user_item_matrix)
user_similarity_df = pd.DataFrame(user_similarity, index=user_item_matrix.index, columns=user_item_matrix.index)

# Recommend movies for a given user
def recommend_movies(user_id, top_n=5):
    # Get similarity scores for this user
    similar_users = user_similarity_df[user_id].drop(user_id).sort_values(ascending=False)
    
    # Weighted ratings from similar users
    weighted_scores = np.dot(similar_users.values, user_item_matrix.loc[similar_users.index])
    
    # Convert to series and normalize
    scores = pd.Series(weighted_scores, index=user_item_matrix.columns)
    already_rated = user_item_matrix.loc[user_id]
    
    # Remove movies the user has already rated
    scores = scores[already_rated == 0].sort_values(ascending=False).head(top_n)
    
    # Return top movie titles
    recommended_movies = movies[movies["movie_id"].isin(scores.index)][["movie_id", "title"]]
    print(f"\nRecommended movies for User {user_id}:\n")
    print(recommended_movies)

    # Store recommendations in database
    with conn.cursor() as cur:
        for movie_id in recommended_movies["movie_id"]:
            cur.execute(
                "INSERT INTO recommendations (user_id, movie_id) VALUES (%s, %s) ON CONFLICT DO NOTHING;",
                (user_id, movie_id)
            )
    conn.commit()

# You must create this table first in pgAdmin
def create_recommendations_table():
    with conn.cursor() as cur:
        cur.execute("""
        CREATE TABLE IF NOT EXISTS recommendations (
            user_id INTEGER,
            movie_id INTEGER,
            PRIMARY KEY (user_id, movie_id),
            FOREIGN KEY (user_id) REFERENCES users(user_id),
            FOREIGN KEY (movie_id) REFERENCES movies(movie_id)
        );
        """)
    conn.commit()

# Run this first time
create_recommendations_table()

# Example usage
recommend_movies(user_id=5, top_n=5)

conn.close()

'''
Output:

Recommended movies for User 5:

     movie_id                              title
6           7              Twelve Monkeys (1995)
55         56                Pulp Fiction (1994)
95         96  Terminator 2: Judgment Day (1991)
126       127              Godfather, The (1972)
194       195             Terminator, The (1984)
'''