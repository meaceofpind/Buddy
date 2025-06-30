from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from .models import Pet, TrackerList, TrackerEntries
from .serializers import PetSerializer, TrackerListSerializer, TrackerEntriesSerializer
from rest_framework.exceptions import NotFound, ValidationError


# List and Create Pets
class PetListCreateAPIView(ListCreateAPIView):
    queryset = Pet.objects.all()
    serializer_class = PetSerializer

    def list(self, request, *args, **kwargs):
        pets = self.get_queryset()
        serializer = self.get_serializer(pets, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        raise ValidationError(serializer.errors)  # Raise validation error for invalid data


# Retrieve, Update, and Delete Pet
class PetRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    queryset = Pet.objects.all()
    serializer_class = PetSerializer

    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
        except Pet.DoesNotExist:
            raise NotFound("Pet not found.")
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)  # partial=True allows partial updates
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        raise ValidationError(serializer.errors)  # Raise validation error for invalid data

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


# List and Create Tracker Lists
class TrackerListListCreateAPIView(generics.ListCreateAPIView):
    queryset = TrackerList.objects.all()
    serializer_class = TrackerListSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        raise ValidationError(serializer.errors)  # Raise validation error for invalid data


# Retrieve, Update, Delete Tracker List
class TrackerListRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = TrackerList.objects.all()
    serializer_class = TrackerListSerializer

    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
        except TrackerList.DoesNotExist:
            raise NotFound("Tracker list not found.")
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        raise ValidationError(serializer.errors)  # Raise validation error for invalid data

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


# List Tracker Lists for a specific Pet
class TrackerListsForPetAPIView(generics.ListAPIView):
    serializer_class = TrackerListSerializer

    def get_queryset(self):
        pet_id = self.kwargs['pet_id']
        if not Pet.objects.filter(pet_id=pet_id).exists():
            raise NotFound("Pet not found.")
        return TrackerList.objects.filter(pet__pet_id=pet_id)


# List and Create Tracker Entries
class TrackerEntriesListCreateAPIView(generics.ListCreateAPIView):
    queryset = TrackerEntries.objects.all()
    serializer_class = TrackerEntriesSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        raise ValidationError(serializer.errors)  # Raise validation error for invalid data


# Retrieve, Update, Delete Tracker Entry
class TrackerEntriesRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = TrackerEntries.objects.all()
    serializer_class = TrackerEntriesSerializer

    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
        except TrackerEntries.DoesNotExist:
            raise NotFound("Tracker entry not found.")
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=False)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        raise ValidationError(serializer.errors)  # Raise validation error for invalid data

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


# List Tracker Entries for a specific Pet
class TrackerEntriesForPetAPIView(generics.ListAPIView):
    serializer_class = TrackerEntriesSerializer

    def get_queryset(self):
        pet_id = self.kwargs['pet_id']
        if not Pet.objects.filter(pet_id=pet_id).exists():
            raise NotFound("Pet not found.")
        return TrackerEntries.objects.filter(pet__pet_id=pet_id)


# List and Create Tracker Entries for a specific pet
class TrackerEntriesForSpecificPetListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = TrackerEntriesSerializer

    def get_queryset(self):
        pet_id = self.kwargs['pet_id']
        if not Pet.objects.filter(pet_id=pet_id).exists():
            raise NotFound("Pet not found.")
        return TrackerEntries.objects.filter(pet__pet_id=pet_id)

    def perform_create(self, serializer):
        pet_id = self.kwargs['pet_id']
        try:
            pet = Pet.objects.get(pet_id=pet_id)
        except Pet.DoesNotExist:
            raise NotFound("Pet not found.")
        serializer.save(pet=pet)


# Retrieve, Update, Delete Tracker Entry for a specific pet
class TrackerEntriesForSpecificPetRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TrackerEntriesSerializer
    lookup_field = 'entry_id'

    def get_queryset(self):
        pet_id = self.kwargs['pet_id']
        if not Pet.objects.filter(id=pet_id).exists():
            raise NotFound("Pet not found.")
        return TrackerEntries.objects.filter(pet__pet_id=pet_id)

    def get_object(self):
        pet_id = self.kwargs['pet_id']
        entry_id = self.kwargs['entry_id']
        try:
            return TrackerEntries.objects.get(pet__pet_id=pet_id, id=entry_id)
        except TrackerEntries.DoesNotExist:
            raise NotFound("Tracker entry not found.")