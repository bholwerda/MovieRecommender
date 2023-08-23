from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Movie, Rating, Recommendation
from .utils import fetch_next_recommendation, build_movie_data, refresh_recommendation

"""
This module contains the test suite for the Movie Recommender application. It includes tests for models, views, 
and utility functions to ensure that the system behaves as expected.

- Models are tested for basic CRUD operations and any custom methods.
- Views are tested to ensure they return the expected results for a given input.
- Utility functions are tested for correctness in a variety of scenarios.
"""


class MovieModelTest(TestCase):
    """Test case for the Movie model."""

    def test_create_movie(self):
        """Ensure that a movie can be properly created and its attributes are as expected."""
        movie = Movie.objects.create(
            title='Inception',
            overview='A thief who enters the dreams of others.',
            genre='Science Fiction',
            poster_url='http://example.com/inception.jpg'
        )
        self.assertEqual(movie.title, 'Inception')


class RatingModelTest(TestCase):
    """Test case for the Rating model."""

    def test_create_rating(self):
        """Ensure that a movie can be properly created and its attributes are as expected."""
        user = User.objects.create_user(username='john_rating', password='123')
        movie = Movie.objects.create(
            title='Inception',
            overview='A thief who enters the dreams of others.',
            genre='Science Fiction',
            poster_url='http://example.com/inception.jpg'
        )
        rating = Rating.objects.create(user=user, movie=movie, rating=5)
        self.assertEqual(rating.rating, 5)


class RecommendationModelTest(TestCase):
    """Test case for the Recommendation model."""

    def setUp(self):
        """Set up test data for recommendation tests."""
        # Create unique usernames for this test case
        self.user1 = User.objects.create_user(username='john_recommend', password='123')
        self.user2 = User.objects.create_user(username='jane_recommend', password='456')

        # Create some movies
        self.movie1 = Movie.objects.create(
            title='Inception',
            overview='A thief who enters the dreams of others.',
            genre='Science Fiction',
            poster_url='http://example.com/inception.jpg'
        )
        self.movie2 = Movie.objects.create(
            title='Interstellar',
            overview='A man goes to space',
            genre='Science Fiction',
            poster_url='http://example.com/interstellar.jpg'
        )

        # Create some ratings for the users
        Rating.objects.create(user=self.user1, movie=self.movie1, rating=5)
        Rating.objects.create(user=self.user1, movie=self.movie2, rating=4)
        Rating.objects.create(user=self.user2, movie=self.movie1, rating=4)

    def test_create_recommendation(self):
        """Ensure that a recommendation can be properly created and its attributes are as expected."""
        user = User.objects.create_user(username='john_create_recommend', password='123')
        movie = Movie.objects.create(
            title='Inception',
            overview='A thief who enters the dreams of others.',
            genre='Science Fiction',
            poster_url='http://example.com/inception.jpg'
        )
        recommendation = Recommendation.objects.create(user=user, movie=movie, score=0.95)
        self.assertEqual(recommendation.score, 0.95)

    def test_get_predictions(self):
        """Ensure that the recommendation system provides accurate movie suggestions."""
        # Get the recommendations for user2
        recommendations = Recommendation.get_predictions(self.user2)

        # Check that the recommendations are as expected
        self.assertEqual(recommendations.iloc[0]['movie_id'], self.movie2.id)

        # Ensure that the recommendations do not include movies that the user has already rated
        rated_movies = Rating.objects.filter(user=self.user2).values_list('movie_id', flat=True)
        for movie_id in rated_movies:
            self.assertNotIn(movie_id, recommendations['movie_id'])


class MovieRecommendationsViewTest(TestCase):
    """Test case for the movie recommendations view."""

    def setUp(self):
        """Set up the test data for movie recommendations view tests."""
        # Create a test user and log them in
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client.login(username='testuser', password='testpass')

        # Create 4 movies to be used in tests
        self.movie1 = Movie.objects.create(title='Movie 1', genre='Action', overview='Description 1')
        self.movie2 = Movie.objects.create(title='Movie 2', genre='Comedy', overview='Description 2')
        self.movie3 = Movie.objects.create(title='Movie 3', genre='Drama', overview='Description 3')
        self.movie4 = Movie.objects.create(title='Movie 4', genre='Horror', overview='Description 4')  # This one will remain unrated

        # Create 3 ratings for the first 3 movies
        self.rating1 = Rating.objects.create(user=self.user, movie=self.movie1, rating=5)
        self.rating2 = Rating.objects.create(user=self.user, movie=self.movie2, rating=4)
        self.rating3 = Rating.objects.create(user=self.user, movie=self.movie3, rating=3)

        # Create 3 recommendations for the movies
        self.recommendation1 = Recommendation.objects.create(user=self.user, movie=self.movie1, score=0.9)
        self.recommendation2 = Recommendation.objects.create(user=self.user, movie=self.movie2, score=0.8)
        self.recommendation3 = Recommendation.objects.create(user=self.user, movie=self.movie3, score=0.7)

    def test_back_action(self):
        """Test the 'back' action logic in the movie recommendations view."""
        response = self.client.get(reverse('get_recommendation'), {'action': 'back', 'movie_id': self.movie2.id})
        data = response.json()
        self.assertEqual(data['recommended_movie']['title'], 'Movie 1')

    def test_next_action_skip(self):
        """Test the 'next' action logic when a movie is skipped in the movie recommendations view."""
        self.rating3.delete()
        response = self.client.get(reverse('get_recommendation'), {'action': 'next', 'movie_id': self.movie3.id})

        # Verify that the movie was marked as skipped for the user
        created_rating = Rating.objects.get(user=self.user, movie=self.movie3)
        self.assertTrue(created_rating.is_skipped)

        # Verify the next recommended movie is returned
        data = response.json()
        self.assertEqual(data['recommended_movie']['title'], 'Movie 1')

    def test_next_action_no_skip(self):
        """Test the 'next' action logic when a movie is not skipped in the movie recommendations view."""
        response = self.client.get(reverse('get_recommendation'), {'action': 'next', 'movie_id': self.movie1.id})
        data = response.json()
        self.assertEqual(data['recommended_movie']['title'], 'Movie 2')

    def test_default_action(self):
        """Test the default action logic when no specific action is provided in the movie recommendations view."""
        response = self.client.get(reverse('get_recommendation'))
        data = response.json()
        self.assertEqual(data['recommended_movie']['title'], 'Movie 1')

    def test_recommendations_view(self):
        """Test the overall behavior of the movie recommendations view."""
        response = self.client.get(reverse('get_recommendation'))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['recommended_movie']['title'], 'Movie 1')


class UtilityFunctionTests(TestCase):
    """Test case for utility functions."""

    def setUp(self):
        """Set up test data for utility function tests."""
        self.user = User.objects.create(username='testuser', password='testpass')
        self.user1 = User.objects.create_user(username='john_recommend', password='123')
        self.user2 = User.objects.create_user(username='jane_recommend', password='456')

        # Create movies
        self.movie1 = Movie.objects.create(title='Movie 1', overview='Overview 1', poster_url='URL 1')
        self.movie2 = Movie.objects.create(title='Movie 2', overview='Overview 2', poster_url='URL 2')
        self.movie3 = Movie.objects.create(title='Movie 3', overview='Overview 3', poster_url='URL 3')
        self.movie4 = Movie.objects.create(title='Movie 4', overview='Overview 4', poster_url='URL 4')

        # Create ratings for some of the movies
        Rating.objects.create(user=self.user, movie=self.movie1, rating=5)
        Rating.objects.create(user=self.user1, movie=self.movie2, rating=3)

    def test_refresh_recommendation(self):
        """Test that the refresh_recommendation utility function correctly refreshes user recommendations."""
        refresh_recommendation(self.user)
        self.assertTrue(Recommendation.objects.filter(user=self.user).exists())

    def test_fetch_next_recommendation_with_existing_recommendation(self):
        """Test that fetch_next_recommendation returns the correct recommendation when one exists."""
        Recommendation.objects.create(user=self.user, movie=self.movie1, score=0.95)
        Recommendation.objects.create(user=self.user, movie=self.movie2, score=0.80)
        data = fetch_next_recommendation(self.user)
        self.assertEqual(data['recommended_movie']['title'], 'Movie 1')
        # Assert that the recommendation for Movie 1 was deleted
        self.assertFalse(Recommendation.objects.filter(user=self.user, movie=self.movie1).exists())

    def test_fetch_next_recommendation_without_existing_recommendation(self):
        """Test that fetch_next_recommendation fetches a new recommendation if none exists."""
        Recommendation.objects.filter(user=self.user).delete()
        data = fetch_next_recommendation(self.user)
        self.assertIn('recommended_movie', data)

    def test_build_movie_data(self):
        """Test that build_movie_data utility function correctly builds movie data."""
        data = build_movie_data(self.movie1)
        self.assertEqual(data['recommended_movie']['title'], 'Movie 1')
        self.assertEqual(data['recommended_movie']['overview'], 'Overview 1')
        self.assertEqual(data['recommended_movie']['poster_url'], 'URL 1')