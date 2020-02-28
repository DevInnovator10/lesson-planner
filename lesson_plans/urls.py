from django.urls import path
from . import views

urlpatterns = [
   path('documents_upload', views.upload_document, name='upload_document'),
   path('search/', views.search_view, name='search_view'),
   path("delete_chat/<int:chat_id>/", views.delete_chat, name="delete_chat"),
]
