# Movie Recommender

## Project Overview

**Movie Recommender** is a portfolio project designed to suggest movies to users based on their previous ratings. Utilizing Python, Django, SQLite, and Scikit-learn's cosine similarity, the application creates a tailored list of movie recommendations for each user. The goal is to enhance the movie-watching experience by suggesting films that align closely with a user's preferences.

### Technologies Used
- Python
- Django
- SQLite
- Scikit-learn (Cosine Similarity)

### Motivation
The project was undertaken to gain practical experience with machine learning and its applications.

## Installation and Setup

### Prerequisites
Ensure you have the `requirements.py` installed in your environment.

### Step-by-Step Instructions
1. Clone the repository
git clone <repo_url>
2. Navigate to the project directory
cd MovieRecommender
3. Install required packages
pip install -r requirements.py
4. Run the Django server
python manage.py runserve


## Usage
To get a feel for the project without creating an account, you can log in using:

- Username: `demouser`
- Password: `demopassword123!`

The application will then display the movie poster, title, and overview of movies for you to rate. Based on your ratings, the algorithm will present you with a new set of recommendations.

**Live Application**: [Movie Recommender App](https://mydjangomovierecommender-887d599fa4e5.herokuapp.com/login/)

## Features
- User account creation and login
- Movie poster display
- Movie title and overview presentation
- 5-point movie rating system
- Movie recommendations based on Cosine Similarity
- Recommendations refresh every 10 movies rated

## Contributing
This is a portfolio project and contributions are not currently being accepted.

## License
This project is under the MIT license. See the LICENSE file for details.

## Contact
For more information or queries related to this project, you can reach out to me at [career.bholwerda@gmail.com](mailto:career.bholwerda@gmail.com).
