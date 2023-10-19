from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from Recommender.models import Recommendation, Rating, Movie
from .forms import UserRegisterForm


# View for user registration
def register(request):
    # If the request method is POST, it means the form has been submitted
    if request.method == 'POST':
        # Creates a form instance with the POST data
        form = UserRegisterForm(request.POST)
        # Checks if the form input is valid
        if form.is_valid():
            # Saves the user and returns the User object
            user = form.save()
            # Calls a function to set initial movie recommendations for the user
            get_initial_movies(user)
            # Retrieves the username from the form
            username = form.cleaned_data.get('username')
            # Sends a success message to be displayed
            messages.success(request, f'Your Account has been created! You are now able to login!')
            # Redirects the user to the login page
            return redirect('login')
    else:
        # If the request method is not POST, it creates an empty form
        form = UserRegisterForm()
    # Renders the registration page with the form
    return render(request, 'users/register.html', {'form': form})


# Function to set initial movie recommendations for a user
def get_initial_movies(user):
    popular_movies = [
        'Air Bud',
        'Spider-Man: Into the Spider-Verse',
        'Black Panther',
        'The Pursuit of Happyness',
        'Inception',
        'Jurassic World Camp Cretaceous',
        'Se7en',
        'Terminator: Dark Fate',
        'Trainspotting',
        'No Country for Old Men',
    ]
    
    movie_objects = Movie.objects.filter(title__in=popular_movies)
    
    recommendations_to_create = [Recommendation(user=user, movie=movie) for movie in movie_objects]

    Recommendation.objects.bulk_create(recommendations_to_create)
