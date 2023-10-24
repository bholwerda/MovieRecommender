from django.db import models
from sklearn.metrics.pairwise import cosine_similarity
from django.contrib.auth.models import User
import numpy as np
import pandas as pd
# Create your models here.


# Movie model representing individual movies in the database
class Movie(models.Model):
    title = models.CharField(max_length=200)
    overview = models.CharField(max_length=2000, null=True)
    genre = models.CharField(max_length=50, null=True)
    poster_url = models.CharField(max_length=200, null=True)

    def __str__(self):
        return self.title


# Rating model representing user ratings for individual movies
class Rating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_ratings')
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='movie_ratings')
    rating = models.IntegerField(blank=True, null=True)
    is_skipped = models.BooleanField(default=False)

    def __str__(self):
        return f' {self.movie.title}: {self.rating}'

# Recommendation model representing movies recommended to users
class Recommendation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    score = models.FloatField(blank=True, null=True)  # Similarity Score based on user-item collaborative filtering

    def __str__(self):
        return self.movie.title
    @classmethod
    def get_predictions(cls, user):
        user_id = user.id
        # Query all ratings from the database
        ratings_query = Rating.objects.filter(is_skipped=False)

        # Convert the QuerySet to a DataFrame for easier manipulation
        ratings_df = pd.DataFrame.from_records(ratings_query.values())

        # Drop the 'id' and 's_skipped' column from the DataFrame as it's not needed for the calculations
        ratings_df = ratings_df.drop('id', axis=1)
        ratings_df = ratings_df.drop('is_skipped', axis=1)

        # Remove duplicates, keeping only the latest entry
        ratings_df = ratings_df.drop_duplicates(subset=['user_id', 'movie_id'], keep='last')

        # Pivot the DataFrame to have users as rows, movies as columns, and ratings as values
        user_movie_matrix = ratings_df.pivot(index='user_id', columns='movie_id', values='rating')

        # Calculate cosine similarities between users based on their ratings. Fill missing values with 0.
        similarities = cosine_similarity(user_movie_matrix.fillna(0))

        # Convert the similarities array to a DF for easier manipulation and set the row and column names to user IDs
        sim_df = pd.DataFrame(data=similarities, index=user_movie_matrix.index, columns=user_movie_matrix.index)

        # Get the similarity scores of the current user with all other users
        user_similarities = sim_df[user_id]

        # Get the IDs of the movies that the user hasn't rated yet
        unrated_movie_ids = user_movie_matrix.loc[user_id][user_movie_matrix.loc[user_id].isnull()].index

        predicted_ratings = {}

        # For each unrated movie
        for movie_id in unrated_movie_ids:
            # Get the ratings of the movie by other users
            other_users_ratings = user_movie_matrix.loc[:, movie_id].dropna()
            # If there are any ratings
            if not other_users_ratings.empty:
                # Calculate a weighted average of the ratings, where the weights are the similarities of the users with the current user
                average = np.nanmean([rating * user_similarities[other_user_id] for other_user_id, rating in
                                      other_users_ratings.items()])
                # Store the predicted rating for the movie
                predicted_ratings[movie_id] = average

        # Convert the predicted ratings to a DataFrame

        predicted_ratings_df = pd.DataFrame.from_records(list(predicted_ratings.items()),
                                                         columns=['movie_id', 'predicted_rating'])

        # Sort the DataFrame by the predicted rating in descending order
        sorted_predicted_ratings_df = predicted_ratings_df.sort_values('predicted_rating', ascending=False)

        # Get the top 10 movies with the highest predicted ratings
        top_movies = sorted_predicted_ratings_df.head(10)

        # Return the top movies
        return top_movies





