from django.urls import path
from SI_Project import views

urlpatterns = [
    path('', views.home, name='home'),
    path('classify/', views.upload_and_classify, name='upload_and_classify'),
    path('segment/', views.upload_and_segment, name='upload_and_segment'),
    path('classify_page/', views.classify_page, name='classify_page'),
    path('segment_page/', views.segment_page, name='segment_page'),
]
