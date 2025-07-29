from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('user_login/', views.user_login, name='user_login'),  # ✅ Ensure this line exists
    path('user_dashboard/', views.user_dashboard, name='user_dashboard'),
    path('admin_login/', views.admin_login, name='admin_login'),
    path('register/', views.register, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('user_logout/', views.user_logout, name='user_logout'),
    path('user_profile/', views.user_profile, name='user_profile'),
    path('predict/', views.predict_engine_health, name='predict_engine_health'),
    path('upload_dataset/', views.upload_dataset, name='upload_dataset'),
    path('train_model/', views.train_models, name='train_model'),
    path('view_users/', views.view_users, name='view_users'),   
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
    
    path('view_recommendations/', views.view_recommendations, name='view_recommendations'),
]
