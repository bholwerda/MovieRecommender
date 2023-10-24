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
        
        non_skipped_ratings = Rating.objects.filter(is_skipped=False)

        ratings_df = pd.DataFrame.from_records(non_skipped_ratings.values())

        ratings_df = ratings_df.drop('id', axis=1)
        ratings_df = ratings_df.drop('is_skipped', axis=1)

        ratings_df = ratings_df.drop_duplicates(subset=['user_id', 'movie_id'], keep='last')

        user_movie_matrix = ratings_df.pivot(index='user_id', columns='movie_id', values='rating')

        similarities = cosine_similarity(user_movie_matrix.fillna(0))

        sim_df = pd.DataFrame(data=similarities, index=user_movie_matrix.index, columns=user_movie_matrix.index)

        user_similarities = sim_df[user_id]

        unrated_movie_ids = user_movie_matrix.loc[user_id][user_movie_matrix.loc[user_id].isnull()].index

        predicted_ratings = {}

        for movie_id in unrated_movie_ids:
            other_users_ratings = user_movie_matrix.loc[:, movie_id].dropna()
            if not other_users_ratings.empty:
                average = np.nanmean([rating * user_similarities[other_user_id] for other_user_id, rating in
                                      other_users_ratings.items()])
                predicted_ratings[movie_id] = average

        predicted_ratings_df = pd.DataFrame.from_records(list(predicted_ratings.items()),
                                                         columns=['movie_id', 'predicted_rating'])

        sorted_predicted_ratings_df = predicted_ratings_df.sort_values('predicted_rating', ascending=False)

        top_movies = sorted_predicted_ratings_df.head(10)

        return top_movies





