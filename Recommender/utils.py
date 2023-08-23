from .models import Recommendation, Movie, Rating

"""
Utility functions for the Recommender app.
These functions assist with fetching and refreshing movie recommendations.
"""


def refresh_recommendation(user):
    """
    Clears the current recommendations for the given user and
    Refreshes the movie recommendations for a given user.
    Calculates new recommendations based on user ratings and stores them in the database.

    Arguments:
    - user: The user for whom recommendations need to be refreshed.
    """
    print('Refreshing recommendations')
    # Fetch new movie recommendations for the user
    recommended_movies = Recommendation.get_predictions(user)
    print(f"Recommendations from get_predictions: {recommended_movies}")

    # Remove old recommendations
    Recommendation.objects.filter(user=user).delete()

    # Store the new recommendations in the database
    for _, row in recommended_movies.iterrows():
        movie_id = row['movie_id']
        predicted_rating = row['predicted_rating']
        recommendation = Recommendation(user=user, movie_id=movie_id, score=predicted_rating)
        recommendation.save()
    print(f"Recommendation objects after refresh: {Recommendation.objects.filter(user=user)}")


def fetch_next_recommendation(user):
    """
    Fetch the next movie recommendation for a given user from the database.
    If there are no stored recommendations, new ones are calculated.

    Parameters:
    - user (User model instance): The user for whom the next recommendation needs to be fetched.

    Returns:
    - context (dict): Contains the next recommended movie details.
    """
    recommendation = Recommendation.objects.filter(user=user).order_by('-score').first()

    # Check if there are no more recommendations
    if not recommendation:
        # No recommendation was found, so we try to refresh recommendations
        refresh_recommendation(user)
        recommendation = Recommendation.objects.filter(user=user).order_by('-score').first()
        print(f"Recommendation after refresh: {recommendation}")

    # Check if a recommendation was found (either initially or after refreshing)
    if recommendation:
        context = build_movie_data(recommendation.movie)
        recommendation.delete()
    else:
        # No recommendations found, even after refreshing
        return {'message': 'No more recommendations available'}

    return context


def build_movie_data(movie):
    """
    Build a dictionary with movie details.
    """
    return {
        'recommended_movie': {
            'title': movie.title,
            'id': movie.id,
            'overview': movie.overview,
            'poster_url': movie.poster_url
        }
    }

