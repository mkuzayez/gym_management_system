from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

urlpatterns = [
    # Authentication endpoints
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Member endpoints
    path('members/', views.MemberListView.as_view(), name='member-list'),
    path('members/<int:pk>/', views.MemberDetailView.as_view(), name='member-detail'),
    path('members/in-gym/', views.InGymMembersView.as_view(), name='members-in-gym'),
    
    # Gym session tracking endpoints
    path('members/<int:pk>/enter/', views.MemberEnterGymView.as_view(), name='member-enter'),
    path('members/<int:pk>/exit/', views.MemberExitGymView.as_view(), name='member-exit'),
    path('sessions/', views.GymSessionListView.as_view(), name='session-list'),
]
