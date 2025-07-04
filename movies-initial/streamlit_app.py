import streamlit as st
import pandas as pd
from scripts.model import get_connection, load_data, get_user_ratings, recommend_movies
import time

st.set_page_config(page_title="🎬 Movie Recommender", layout="wide")
st.title("🎥 Movie Recommender System")

# 1. Maintain user_id in session
if "user_id" not in st.session_state:
    st.session_state.user_id = None

# Input once
if st.session_state.user_id is None:
    user_input = st.number_input("Enter User ID", min_value=1, max_value=943, step=1)
    if st.button("Get Recommendations"):
        st.session_state.user_id = user_input
        st.rerun()

# 2. Main app logic inside a function
def run_app(user_id):
    conn = get_connection()
    ratings, movies = load_data(conn)

    st.subheader("📊 User's Past Ratings")
    user_rated = get_user_ratings(user_id, ratings, movies)
    if user_rated.empty:
        st.write("No ratings found.")
    else:
        st.dataframe(user_rated)

    st.subheader("🤖 Recommended Movies")
    recommendations = recommend_movies(user_id, ratings, movies)

    # Remove movies already rated
    rated_movie_ids = ratings[ratings["user_id"] == user_id]["movie_id"].tolist()
    recommendations = recommendations[~recommendations["title"].isin(user_rated["title"])]

    if recommendations.empty:
        st.success("🎉 You've rated all your recommendations!")
    else:
        with conn.cursor() as cur:
            for idx, row in recommendations.iterrows():
                movie_title = row["title"]
                movie_id = movies[movies["title"] == movie_title]["movie_id"].values[0]

                col1, col2 = st.columns([3, 2])
                with col1:
                    st.write(f"🎬 {movie_title}")
                with col2:
                    rating = st.selectbox(
                        f"Rate",
                        options=[None, 1, 2, 3, 4, 5],
                        key=f"rate_{movie_id}"
                    )
                    if rating is not None:
                        if st.button(f"Submit for '{movie_title}'", key=f"submit_{movie_id}"):
                            timestamp = int(time.time())
                            try:
                                cur.execute(
                                    """
                                    INSERT INTO ratings (user_id, movie_id, rating, timestamp)
                                    VALUES (%s, %s, %s, %s)
                                    ON CONFLICT (user_id, movie_id) DO UPDATE
                                    SET rating = EXCLUDED.rating, timestamp = EXCLUDED.timestamp;
                                    """,
                                    (int(user_id), int(movie_id), int(rating), int(timestamp))
                                )
                                conn.commit()
                                st.success(f"✅ Rating saved for '{movie_title}'")
                                time.sleep(1)
                                st.rerun()  # force fresh fetch
                            except Exception as e:
                                st.error(f"Error: {e}")

    conn.close()

# Run main logic if user ID is available
if st.session_state.user_id:
    run_app(st.session_state.user_id)
