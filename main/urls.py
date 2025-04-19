from django.urls import path
from .views import *

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', CustomTokenObtainPairView.as_view(), name='token-obtain-pair'),
    path('token/refresh', TokenRefreshView.as_view(), name='token-refresh'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('create-session/', CreateSessionView.as_view(), name='create-session'),
    path('list-sessions/', ListSessionsView.as_view(), name='list-sessions'),
    path('edit-session/', EditSessionView.as_view(), name='edit-session'),
    path('create-exercise/', CreateExerciseView.as_view(), name='create-exercise'),
    path('list-exercises/', ListExercisesView.as_view(), name='list-exercises'),
    path('edit-exercise/', EditExerciseView.as_view(), name='edit-exercise'),
]