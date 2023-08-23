from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from Recommender.models import Recommendation, Rating
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
    print("get_initial_movies function is being called!")  # Add this line
    # Retrieves the base user from the User model
    base_user = User.objects.get(username='brett')
    # Retrieves the top 9 rated movies from the base user
    popular_ratings = Rating.objects.filter(user=base_user).order_by('-rating')[:10]
    # Retrieves the movie objects associated with the popular ratings
    popular_movies = [r.movie for r in popular_ratings]

    # Iterates over each popular movie
    for movie in popular_movies:
        # Creates a recommendation for the user and the movie
        Recommendation.objects.create(user=user, movie=movie)
