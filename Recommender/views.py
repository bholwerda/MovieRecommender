from django.shortcuts import render, get_object_or_404
import json
from django.http import JsonResponse
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from .models import User, Movie, Rating
from .utils import fetch_next_recommendation, build_movie_data


class Home(LoginRequiredMixin, TemplateView):
    template_name = 'Recommender/home.html'

    def get(self, request, *args, **kwargs):
        '''
        Handles the GET request for the Home view. Fetches the next movie
        recommendation for the user and renders it using the template.
        '''
        user = request.user
        context = fetch_next_recommendation(user)

        return render(request, self.template_name, context)


def rate_movie(request):
    if request.method == 'POST':
        data = json.loads(request.body)

        # Extract movie details and user rating from the POST data
        movie_id = data.get('movie_id')
        user_id = data.get('user_id')
        rating_value = data.get('rating')

        try:
            movie = Movie.objects.get(id=movie_id)
            user = User.objects.get(id=user_id)
        except Movie.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Movie does not exist'})
        except User.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'User does not exist'})

        try:
            rating = Rating.objects.get(user=user, movie=movie)
            rating.rating = rating_value
            rating.is_skipped = False
            rating.save()
        except ObjectDoesNotExist:
            # Create and save the rating
            rating = Rating(user=user, movie=movie, rating=rating_value)
            rating.save()

        return JsonResponse({'status': 'success'})
    else:
        return JsonResponse({'status': 'error'})


def get_recommendation(request):
    """
    View to fetch the next movie recommendation for a user.
    Also handles going back to a previously rated movie.
    """
    if request.method == 'GET':

        user = request.user
        action = request.GET.get('action')

        # Handle 'back' action
        if action == 'back':
            current_id = request.GET.get('movie_id')
            # Try to get the current rating for the given movie_id and user
            try:
                current_rating = Rating.objects.get(movie__id=current_id, user=user)
            except Rating.DoesNotExist:
                current_rating = None
            except Rating.MultipleObjectsReturned:
                # If multiple ratings are found, use the latest one
                current_rating = Rating.objects.filter(movie__id=current_id, user=user).latest('id')

            if current_rating:
                previous_ratings = Rating.objects.filter(user=user, id__lt=current_rating.id).order_by('-id')
                previous_movie = previous_ratings.first()
            else:
                previous_movie = Rating.objects.filter(user=user).last()

            if previous_movie:
                data = build_movie_data(previous_movie.movie)
                return JsonResponse(data)
            else:
                return JsonResponse({'message': 'No previous movie available'})

        elif action == 'next':
            movie_id = request.GET.get('movie_id')

            # Check for current rating for the given movie_id and user for navigation to previous movies
            try:
                current_rating = Rating.objects.get(movie__id=movie_id, user=user)
            except Rating.DoesNotExist:
                current_rating = None
            except Rating.MultipleObjectsReturned:
                # If multiple ratings are found, use the latest one
                current_rating = Rating.objects.filter(movie__id=movie_id, user=user).latest('id')

            next_movie = None
            if current_rating:
                next_movie_ratings = Rating.objects.filter(user=user, id__gt=current_rating.id).order_by('id')
                next_movie = next_movie_ratings.first()
            else:
                # If the movie does not exist, return an error response with status code 404
                movie = get_object_or_404(Movie, id=movie_id)
                Rating.objects.create(user=user, movie=movie, is_skipped=True)

            if next_movie:
                data = build_movie_data(next_movie.movie)
                return JsonResponse(data)
            else:
                data = fetch_next_recommendation(user)
                return JsonResponse(data)

        else:
            data = fetch_next_recommendation(user)
            return JsonResponse(data)


