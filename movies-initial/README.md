# 🎬 Movie Recommender System

A simple user-based collaborative filtering system using the MovieLens 100K dataset. Built with Python and PostgreSQL.

## 📦 Features

- Load MovieLens data into PostgreSQL
- Explore data with summary stats and plots
- Recommend movies using cosine similarity between users
- Command-line interface for personalized recommendations
- Save recommendations to PostgreSQL

## 🚀 Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/movie-recommender.git
   cd movie-recommender```

2. Install Python dependencies:
    ```
    bash
    Copy
    Edit
    pip install -r requirements.txt
    ```
3. Set up PostgreSQL:
    Create a DB named movielens
    Create the required tables using scripts/load_data.py

4. Run the CLI:
    ```bash
    Copy
    Edit
    python scripts/cli_recommender.py```