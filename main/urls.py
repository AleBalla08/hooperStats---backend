from django.urls import path
from .views import *

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login-view'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('protected/', ProtectedView.as_view(), name='protected'),
    path('token/refresh/', RefreshTokenView.as_view(), name='token_refresh'),
    path('create-session/', CreateSessionView.as_view(), name='create-session'),
    path('list-sessions/', ListSessionsView.as_view(), name='list-sessions'),
    path('edit-session/', EditSessionView.as_view(), name='edit-session'),
    path('remove-session/', RemoveSessionView.as_view(), name='remove-session'),
    path('create-goal/', CreateTask.as_view(), name='create-goal'),
    path('list-goals/', ListTasksView.as_view(), name='list-goals'),
    path('edit-goal/', EditTaskView.as_view(), name='edit-goal'),
    path('clear-checked-goals/', ClearCheckedTasksView.as_view(), name='clear-checked-goals'),

    #single session
    path('session/', SingleSessionListView.as_view(), name='session'),
    path('create-exercise/', CreateExerciseView.as_view(), name='create-exercise'),
    path('edit-exercise/<str:id>', EditExerciseView.as_view(), name='edit-exercise'),
    path('end-session/<str:id>', EndSessionView.as_view(), name='end-session'),
    path('get-done-sessions/', GetDoneSessionsView.as_view(), name='get-done-sessions'),
    path('clear-done-sessions/', ClearDoneSessionsView.as_view(), name='clear-done-sessions')
]