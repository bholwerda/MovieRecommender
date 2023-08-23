from django.contrib import admin
from .models import Movie, Recommendation, Rating


# Admin view for the Movie model
class MovieAdmin(admin.ModelAdmin):
    # Display these fields in the admin list view
    list_display = ('id', 'title', 'overview', 'genre', 'poster_url')
    # Enable search functionality based on these fields
    search_fields = ('title', 'genre',)
    # Allow filtering the list view by these fields
    list_filter = ('genre',)

# Admin view for the Rating model
class RatingAdmin(admin.ModelAdmin):
    # Display these fields in the admin list view
    list_display = ('id', 'user', 'movie', 'rating', 'is_skipped')
    # Enable search functionality based on the 'user' and 'movie' fields
    search_fields = ('user__username', 'movie__title',)
    # Allow filtering the list view by the 'is_skipped' field
    list_filter = ('is_skipped',)

# Admin view for the Recommendation model
class RecommendationAdmin(admin.ModelAdmin):
    # Display these fields in the admin list view
    list_display = ('id', 'user', 'movie', 'score')
    # Enable search functionality based on the 'user' and 'movie' fields
    search_fields = ('user__username', 'movie__title',)

# Register the models and their corresponding admin views
admin.site.register(Movie, MovieAdmin)
admin.site.register(Rating, RatingAdmin)
admin.site.register(Recommendation, RecommendationAdmin)
