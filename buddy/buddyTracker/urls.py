from django.urls import path
from .views_api import (
    PetListCreateAPIView, 
    PetRetrieveUpdateDestroyAPIView,
    TrackerListListCreateAPIView,
    TrackerListRetrieveUpdateDestroyAPIView,
    TrackerListsForPetAPIView,
    TrackerEntriesListCreateAPIView,
    TrackerEntriesRetrieveUpdateDestroyAPIView,
    TrackerEntriesForPetAPIView,
    TrackerEntriesForSpecificPetListCreateAPIView,
    TrackerEntriesForSpecificPetRetrieveUpdateDestroyAPIView

    )
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

from .views_ui import edit_entry, edit_tracker, home, trackers_list, tracker_entries, new_tracker, new_entry

urlpatterns = [
    path('api/pets/', PetListCreateAPIView.as_view(), name='pet-list-create'),  
    path('api/pets/<str:pk>/', PetRetrieveUpdateDestroyAPIView.as_view(), name='pet-detail'),  
    path('api/trackerlists/', TrackerListListCreateAPIView.as_view(), name='trackerlist-list-create'),  
    path('api/trackerlists/<str:pk>/', TrackerListRetrieveUpdateDestroyAPIView.as_view(), name='trackerlist-detail'),  
    path('api/pets/<str:pet_id>/trackerlists/', TrackerListsForPetAPIView.as_view(), name='trackerlists-for-pet'),
    path('api/trackerentries/', TrackerEntriesListCreateAPIView.as_view(), name='trackerentries-list-create'),
    path('api/trackerentries/<int:pk>/', TrackerEntriesRetrieveUpdateDestroyAPIView.as_view(), name='trackerentries-detail'),
    path('api/pets/<str:pet_id>/trackerentries/', TrackerEntriesForPetAPIView.as_view(), name='trackerentries-for-pet'),
    path('api/pets/<str:pet_id>/trackerentries/all/', TrackerEntriesForSpecificPetListCreateAPIView.as_view(), name='trackerentries-for-specific-pet-list-create'),
    path('api/pets/<str:pet_id>/trackerentries/detail/<int:entry_id>/', TrackerEntriesForSpecificPetRetrieveUpdateDestroyAPIView.as_view(), name='trackerentries-for-specific-pet-detail'),


    
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),  
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),  
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

    path('', home, name="home"),
    path('pets/<str:pet_id>/trackers/', trackers_list, name="trackers_list"),
    path('trackers/<int:tracker_id>/entries/', tracker_entries, name="tracker_entries"),
    path('pets/<str:pet_id>/trackers/new/', new_tracker, name="new_tracker"),
    path('trackers/<int:tracker_id>/edit/', edit_tracker, name='edit_tracker'),
    path('trackers/<int:tracker_id>/entries/new/', new_entry, name="new_entry"),
    path('trackers/<int:tracker_id>/entries/<int:entry_id>/edit/', edit_entry, name="edit_entry"),
]


