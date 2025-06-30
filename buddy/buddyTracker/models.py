from django.db import models
import json, random, string
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

def generate_uid(length=6):
    """Generate a random UID of specified length (default: 6)."""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

class Pet(models.Model):
    pet_id= models.CharField(
        max_length=6,  
        primary_key=True,  
        unique=True,
        default=generate_uid,  
        editable=False
    )

    name = models.CharField(
        max_length=100,
        verbose_name="Pet Name",
        help_text="Enter the pet's name"
    )
    
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
    ]
    gender = models.CharField(
        max_length=1,
        choices=GENDER_CHOICES,
        verbose_name="Pet Gender",
        help_text="Select the pet's gender"
    )
    
    age = models.PositiveIntegerField(
        verbose_name="Pet Age",
        help_text="Enter the pet's age in years"
    )
    
    species = models.CharField(
        max_length=50,
        choices=[
            ('Dog','Dog'),
            ('Cat','Cat')
        ],
        verbose_name="Species",
        help_text="Enter the species of the pet"
    )

    breed = models.CharField(
        max_length=50,
        verbose_name="Breed",
        help_text="Enter the breed of the pet"
    )
    
    last_modified = models.DateTimeField(
        auto_now=True,
        editable=False, 
        verbose_name="Last Modified",
        help_text="The date and time when this record was last modified"
    )

    def __str__(self):
        return f"{self.name}"

class FormOption(models.Model):
    tracker = models.ForeignKey(
        'TrackerList',
        on_delete=models.CASCADE,
        related_name='options',
        verbose_name="Tracker"
    )
    field_name = models.CharField(
        max_length=100,
        verbose_name="Field Name",
        help_text="Enter the field name (e.g., Vaccination Date, Treatment Cost)"
    )
    field_type = models.CharField(
        max_length=50,
        choices=[
            ('CharField', 'Text'),
            ('DateField', 'Date'),
            ('FloatField', 'Decimal Number'),
            ('IntegerField', 'Integer Number'),
            ('ImageField', 'Image'),
        ],
        verbose_name="Field Type",
        help_text="Select the data type for the field"
    )

    def __str__(self):
        return f"{self.field_name} ({self.field_type})"

class TrackerList(models.Model):
    name = models.CharField(
        max_length=100,
        verbose_name="Tracker Name",
        help_text="Enter the name of the tracker (e.g., Vaccination, Treatment)"
    )
    
    pet = models.ForeignKey(
        'Pet',
        on_delete=models.CASCADE,
        related_name='tracker_lists',
        verbose_name="Pet",
        help_text="Select the pet associated with this tracker"
    )
    
    def clean(self):
        if not self.pk:  # Avoid running validation when object is not saved
            return

        options = list(self.options.all())  

        if not options:
            raise ValidationError("At least one form field (option) is required for the tracker.")

        field_names = set()
        allowed_field_types = {'CharField', 'DateField', 'FloatField', 'IntegerField'}

        for option in options:
            if option.field_name in field_names:
                raise ValidationError(f"Duplicate field name '{option.field_name}' found.")
            field_names.add(option.field_name)

            if option.field_type not in allowed_field_types:
                raise ValidationError(f"Invalid field type '{option.field_type}'.")


        def __str__(self):
            return f"{self.name} (Pet ID: {self.pet_id})"
        
class TrackerEntryImage(models.Model):
    entry = models.ForeignKey('TrackerEntries', on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='entry_images/')

class TrackerEntryData(models.Model):
    entry = models.ForeignKey(
        'TrackerEntries',
        on_delete=models.CASCADE,
        related_name='data',
        verbose_name="Entry"
    )
    field_name = models.CharField(max_length=100, verbose_name="Field Name")
    field_type = models.CharField(max_length=50, verbose_name="Field Type")  # Will match form options
    field_value = models.JSONField(verbose_name="Field Value (Dynamic)", help_text="Store the value in appropriate data type")

    def clean(self):
        """ Ensure that the field type matches the form options in TrackerList. """
        # Get the tracker list associated with this entry
        tracker_list = self.entry.tracker  # Assuming TrackerEntries has a foreign key to TrackerList

        # Ensure the number of TrackerEntryData matches the number of FormOptions in the associated TrackerList
        if tracker_list:
            # Fetch form options related to the tracker list this entry is associated with
            form_options = tracker_list.options.all()

            # Check if the current entry is being created (to avoid validation on updates)
            if not self.pk:  # Only validate on creation
                # Check if the number of TrackerEntryData matches the number of FormOptions
                if tracker_list.options.count() != self.entry.data.count() + 1:  # Adding 1 for the current entry being created
                    raise ValidationError(_("Number of TrackerEntryData must match the number of options in TrackerList."))

            # Check if the submitted field_type matches one of the valid types
            valid_field_types = {opt.field_type for opt in form_options}
            if self.field_type not in valid_field_types:
                raise ValidationError(_("Field type must be one of the defined types in TrackerList options."))

            # Validate the value based on the field_type
            if self.field_type == 'CharField' and not isinstance(self.field_value, str):
                raise ValidationError(_("Field value must be a string for CharField."))
            elif self.field_type == 'DateField' and not self._is_valid_date(self.field_value):
                raise ValidationError(_("Field value must be a valid date for DateField."))
            elif self.field_type == 'IntegerField' and not isinstance(self.field_value, int):
                raise ValidationError(_("Field value must be an integer for IntegerField."))
            elif self.field_type == 'FloatField' and not isinstance(self.field_value, float):
                raise ValidationError(_("Field value must be a float for FloatField."))

    def _is_valid_date(self, value):
        """ Check if the value is a valid date. """
        try:
            json.loads(json.dumps(value, default=str))  # Simple check to serialize date format
            return True
        except (TypeError, ValueError):
            return False
    
    def __str__(self):
        return f"{self.field_name}: {self.field_value}"

class TrackerEntries(models.Model):
    tracker = models.ForeignKey(
        TrackerList,
        on_delete=models.CASCADE, 
        related_name='entries'
    )
    pet = models.ForeignKey(
        Pet, 
        on_delete=models.CASCADE, 
        related_name='pet_entries'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        if not self.pk:
            return

        tracker = self.tracker
        form_options = list(tracker.options.all())  # Convert to list
        tracker_entry_data = list(self.data.all())  # Convert to list

        if len(tracker_entry_data) != len(form_options):
            raise ValidationError(f"Mismatch: {len(tracker_entry_data)} entries vs {len(form_options)} fields.")

        form_options_dict = {opt.field_name: opt.field_type for opt in form_options}

        for entry_data in tracker_entry_data:
            expected_type = form_options_dict.get(entry_data.field_name)

            if expected_type is None:
                raise ValidationError(f"Field '{entry_data.field_name}' is not in the tracker.")

            if expected_type != entry_data.field_type:
                raise ValidationError(f"Mismatch for '{entry_data.field_name}': Expected {expected_type}, got {entry_data.field_type}.")
    
    def __str__(self):
        return f"Entry for Tracker {self.tracker_id}"