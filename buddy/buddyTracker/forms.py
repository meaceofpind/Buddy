from django import forms
from .models import TrackerList, TrackerEntries

class TrackerForm(forms.ModelForm):
    class Meta:
        model = TrackerList
        fields = ["name"]

class TrackerEntryForm(forms.ModelForm):
    class Meta:
        model = TrackerEntries
        fields = []