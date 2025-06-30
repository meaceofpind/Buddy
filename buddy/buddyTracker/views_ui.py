from django.shortcuts import get_object_or_404, render, redirect
from django.conf import settings
from django.http import HttpRequest
from buddyTracker.models import TrackerEntryData, TrackerEntryImage
from rest_framework.request import Request
from rest_framework.test import APIRequestFactory
from .forms import TrackerForm, TrackerEntryForm
from .views_api import *
from urllib.parse import urlparse

import logging

logger = logging.getLogger(__name__)

api_factory = APIRequestFactory()

def home(request):
    """Fetch pet list using API view."""
    api_request = api_factory.get("/")  # Mimic an API GET request
    api_view = PetListCreateAPIView.as_view()
    response = api_view(api_request)

    pets = response.data if response.status_code == 200 else []
    return render(request, "home.html", {"pets": pets})

def trackers_list(request, pet_id):
    """Fetch trackers for a specific pet using API function"""

    # Fetch pet details
    pet_view = PetRetrieveUpdateDestroyAPIView.as_view()
    pet_request = api_factory.get(f"/api/pets/{pet_id}/")  # Create API request
    pet_response = pet_view(pet_request, pk=pet_id)

    pet = pet_response.data if pet_response.status_code == 200 else None

    # Fetch trackers for the pet
    tracker_view = TrackerListsForPetAPIView.as_view()
    tracker_request = api_factory.get(f"/api/pets/{pet_id}/trackerlists/")
    tracker_response = tracker_view(tracker_request, pet_id=pet_id)

    trackers = tracker_response.data if tracker_response.status_code == 200 else []

    # ✅ Pass Django's `request` (not DRF's Request)
    return render(request, "trackers_list.html", {"pet": pet, "trackers": trackers})

def tracker_entries(request, tracker_id):
    """Fetch tracker entries for a specific tracker using API view."""
    tracker = get_object_or_404(TrackerList, id=tracker_id)
    pet_id = tracker.pet.pet_id  # Correct pet_id

    api_request = api_factory.get(f"/api/pets/{pet_id}/trackerentries/")
    api_view = TrackerEntriesForPetAPIView.as_view()
    response = api_view(api_request, pet_id=pet_id)  # ✅ use pet_id here

    all_entries = response.data if response.status_code == 200 else []
    current_host = request.get_host()

    for entry in all_entries:
        if "images" in entry:
            for img in entry["images"]:
                if "image" in img:
                    parsed_url = urlparse(img["image"])
                    if parsed_url.netloc and parsed_url.netloc != current_host:
                        corrected_url = parsed_url._replace(netloc=current_host).geturl()
                        img["image"] = corrected_url

    entries = [entry for entry in all_entries if entry["tracker"] == tracker_id]

    return render(request, "tracker_entries.html", {
        "tracker": tracker,
        "entries": entries,
        "MEDIA_URL": settings.MEDIA_URL
    })

def new_tracker(request, pet_id):
    """Create a new tracker using API view."""
    if request.method == "POST":
        form = TrackerForm(request.POST)
        if form.is_valid():
            options = []
            index = 0
            while True:
                field_name = request.POST.get(f"options[{index}][field_name]")
                field_type = request.POST.get(f"options[{index}][field_type]")
                if not field_name or not field_type:
                    break
                options.append({
                    "field_name": field_name,
                    "field_type": field_type
                })
                index += 1

            payload = {
                **form.cleaned_data,
                "pet_id": pet_id,
                "options": options
            }
            api_request = api_factory.post("/api/trackerlists/", data=payload, format="json")
            api_view = TrackerListListCreateAPIView.as_view()
            response = api_view(api_request)

            if response.status_code == 201:
                return redirect("trackers_list", pet_id=pet_id)

    else:
        form = TrackerForm()
    
    return render(request, "new_tracker.html", {"form": form})

def edit_tracker(request, tracker_id):
    tracker = get_object_or_404(TrackerList, id=tracker_id)

    if request.method == "POST":
        form = TrackerForm(request.POST, instance=tracker)
        if form.is_valid():
            options = []
            index = 0
            while True:
                field_name = request.POST.get(f"options[{index}][field_name]")
                field_type = request.POST.get(f"options[{index}][field_type]")
                if not field_name or not field_type:
                    break
                options.append({
                    "field_name": field_name,
                    "field_type": field_type
                })
                index += 1

            payload = {
                **form.cleaned_data,
                "options": options
            }

            api_request = api_factory.put(f"/api/trackerlists/{tracker_id}/", data=payload, format="json")
            api_view = TrackerListRetrieveUpdateDestroyAPIView.as_view()
            response = api_view(api_request, pk=tracker_id)

            if response.status_code == 200:
                return redirect("trackers_list", pet_id=tracker.pet.pet_id)
    else:
        form = TrackerForm(instance=tracker)

    return render(request, "edit_tracker.html", {
        "form": form,
        "tracker": tracker
    })

def new_entry(request, tracker_id):
    tracker = get_object_or_404(TrackerList, id=tracker_id)
    options = tracker.options.all()

    if request.method == "POST":
        if not tracker.pet:
            return render(request, "error.html", {
                "message": "This tracker is not associated with any pet. Please assign a pet before adding entries."
            })

        data = []
        images = {}

        for opt in options:
            if opt.field_type == "ImageField":
                val = request.FILES.get(opt.field_name)
                if val:
                    images[opt.field_name] = val
                field_value = val.name if val else ""
            else:
                field_value = request.POST.get(opt.field_name)

            data.append({
                "field_name": opt.field_name,
                "field_type": opt.field_type,
                "field_value": field_value
            })

        payload = {
            "tracker": tracker.id,
            "pet": tracker.pet.pet_id,  # using custom primary key
            "data": data
        }

        api_request = api_factory.post(
            f"/api/pets/{tracker.pet.pet_id}/trackerentries/all/", data=payload, format="json"
        )
        api_view = TrackerEntriesForSpecificPetListCreateAPIView.as_view()
        response = api_view(api_request, pet_id=tracker.pet.pet_id)

        if response.status_code == 201:
            entry_id = response.data["id"]
            entry = TrackerEntries.objects.get(id=entry_id)

            # Save uploaded images
            for name, image_file in images.items():
                TrackerEntryImage.objects.create(entry=entry, image=image_file)

            return redirect("tracker_entries", tracker_id=tracker_id)

    return render(request, "new_entry.html", {
        "tracker": tracker,
        "options": options
    })

def edit_entry(request, tracker_id, entry_id):
    tracker = get_object_or_404(TrackerList, id=tracker_id)
    entry = get_object_or_404(TrackerEntries, id=entry_id, tracker_id=tracker_id)
    options = tracker.options.all()

    if request.method == "POST":
        data = []
        images = {}

        for opt in options:
            if opt.field_type == "ImageField":
                val = request.FILES.get(opt.field_name)
                if val:
                    images[opt.field_name] = val
                field_value = val.name if val else ""
            else:
                field_value = request.POST.get(opt.field_name)

            data.append({
                "field_name": opt.field_name,
                "field_type": opt.field_type,
                "field_value": field_value
            })

        payload = {
            "tracker": tracker.id,
            "pet": tracker.pet.id,
            "data": data
        }

        api_request = api_factory.put(
            f"/api/trackerentries/{entry.id}/", data=payload, format="json"
        )
        api_view = TrackerEntriesRetrieveUpdateDestroyAPIView.as_view()
        response = api_view(api_request, pk=entry.id)

        if response.status_code == 200:
            # Delete existing images (optional)
            entry.images.all().delete()

            # Save new images
            for name, image_file in images.items():
                TrackerEntryImage.objects.create(entry=entry, image=image_file)

            return redirect("tracker_entries", tracker_id=tracker_id)

    initial_data = {d.field_name: d.field_value for d in entry.data.all()}
    return render(request, "edit_entry.html", {
        "tracker": tracker,
        "options": options,
        "initial_data": initial_data,
        "entry": entry,
    })