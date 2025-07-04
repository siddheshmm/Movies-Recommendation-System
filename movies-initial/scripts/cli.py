import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import psycopg2

# Database connection
conn = psycopg2.connect(
    dbname="movielens100k",
    user="postgres",
    password="siddhesh",
    host="localhost",
    port="5432"
)

def load_data():
    ratings = pd.read_sql("SELECT * FROM ratings", conn)
    movies = pd.read_sql("SELECT * FROM movies", conn)
    return ratings, movies

def get_user_ratings(user_id, ratings, movies):
    user_rated = ratings[ratings["user_id"] == user_id]
    return user_rated.merge(movies, on="movie_id")[["title", "rating"]]

def get_recommendations(user_id, ratings, movies, top_n=5):
    user_item_matrix = ratings.pivot(index="user_id", columns="movie_id", values="rating").fillna(0)
    user_similarity = cosine_similarity(user_item_matrix)
    similarity_df = pd.DataFrame(user_similarity, index=user_item_matrix.index, columns=user_item_matrix.index)

    if user_id not in similarity_df.index:
        print("❌ Invalid user_id.")
        return pd.DataFrame()

    similar_users = similarity_df[user_id].drop(user_id).sort_values(ascending=False)
    weighted_scores = np.dot(similar_users.values, user_item_matrix.loc[similar_users.index])
    scores = pd.Series(weighted_scores, index=user_item_matrix.columns)

    already_rated = user_item_matrix.loc[user_id]
    scores = scores[already_rated == 0].sort_values(ascending=False).head(top_n)

    recommended_movies = movies[movies["movie_id"].isin(scores.index)]
    
    # Store recommendations
    with conn.cursor() as cur:
        for movie_id in recommended_movies["movie_id"]:
            cur.execute(
                "INSERT INTO recommendations (user_id, movie_id) VALUES (%s, %s) ON CONFLICT DO NOTHING;",
                (user_id, movie_id)
            )
    conn.commit()
    
    return recommended_movies[["title"]]

def main():
    ratings, movies = load_data()
    user_id = int(input("Enter user ID: "))

    print("\n🎞️  Your past ratings:")
    user_ratings = get_user_ratings(user_id, ratings, movies)
    if user_ratings.empty:
        print("No ratings found.")
    else:
        print(user_ratings)

    print("\n🤖 Recommended movies for you:")
    recs = get_recommendations(user_id, ratings, movies)
    if recs.empty:
        print("No recommendations found.")
    else:
        print(recs)

if __name__ == "__main__":
    main()

"""
Enter user ID: 10

🎞️  Your past ratings:
                                  title  rating
0    French Twist (Gazon maudit) (1995)       4
1                        Sabrina (1954)       4
2                         Brazil (1985)       3
3                          Laura (1944)       5
4                 Twelve Monkeys (1995)       4
..                                  ...     ...
179             Perfect World, A (1993)       4
180        It Happened One Night (1934)       4
181     Welcome to the Dollhouse (1995)       4
182             Dead Man Walking (1995)       4
183     Nikita (La Femme Nikita) (1990)       3

[184 rows x 2 columns]

🤖 Recommended movies for you:
                               title
78              Fugitive, The (1993)
171  Empire Strikes Back, The (1980)
180        Return of the Jedi (1983)
203        Back to the Future (1985)
318          Schindler's List (1993)
"""