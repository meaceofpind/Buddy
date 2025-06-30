from rest_framework import serializers
from .models import Pet, TrackerList, TrackerEntries, FormOption, TrackerEntryData, TrackerEntryImage

class PetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pet
        fields = ['pet_id', 'name', 'gender', 'age', 'species', 'last_modified']
        read_only_fields = ['last_modified']  

class FormOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = FormOption
        fields = ['field_name', 'field_type']

    def validate_options(self, value):
        allowed_field_types = ['CharField', 'DateField', 'FloatField', 'IntegerField']
        
        if not isinstance(value, list):
            raise serializers.ValidationError("Options must be a list of field definitions.")

        for field in value:
            if not isinstance(field, dict):
                raise serializers.ValidationError("Each option must be a dictionary.")
            if 'field_name' not in field or not field['field_name']:
                raise serializers.ValidationError("Each option must have a 'field_name'.")
            if 'field_type' not in field or field['field_type'] not in allowed_field_types:
                raise serializers.ValidationError(f"Invalid field type: {field.get('field_type')}")
        
        return value

class TrackerListSerializer(serializers.ModelSerializer):
    pet = PetSerializer(read_only=True)  
    pet_id = serializers.PrimaryKeyRelatedField(
        queryset=Pet.objects.all(), source='pet', write_only=True, allow_null=False
    )
    options = FormOptionSerializer(many=True)

    class Meta:
        model = TrackerList
        fields = ['id', 'name', 'pet', 'pet_id', 'options']

    def create(self, validated_data):
        options_data = validated_data.pop('options')
        tracker = TrackerList.objects.create(**validated_data)
        for option in options_data:
            FormOption.objects.create(tracker=tracker, **option)
        return tracker
    
    def update(self, instance, validated_data):
        options_data = validated_data.pop('options', [])
        
        # Update tracker basic fields
        instance.name = validated_data.get('name', instance.name)
        instance.pet = validated_data.get('pet', instance.pet)
        instance.save()

        # Clear existing options and recreate them
        instance.options.all().delete()
        for option in options_data:
            FormOption.objects.create(tracker=instance, **option)

        return instance

    
class TrackerEntryImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrackerEntryImage
        fields = ['id', 'image']

class TrackerEntryDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrackerEntryData
        fields = ['field_name', 'field_type', 'field_value']


class TrackerEntriesSerializer(serializers.ModelSerializer):
    tracker = serializers.PrimaryKeyRelatedField(queryset=TrackerList.objects.all())
    pet = serializers.PrimaryKeyRelatedField(queryset=Pet.objects.all())
    data = TrackerEntryDataSerializer(many=True)
    images = TrackerEntryImageSerializer(many=True, read_only=True)

    class Meta:
        model = TrackerEntries
        fields = ['id', 'tracker', 'pet', 'data', 'created_at', 'images']

    def create(self, validated_data):
        data_items = validated_data.pop('data')
        entry = TrackerEntries.objects.create(**validated_data)

        for item in data_items:
            TrackerEntryData.objects.create(entry=entry, **item)

        return entry
    
    def update(self, instance, validated_data):
        data_items = validated_data.pop('data', [])

        # Update basic fields
        instance.tracker = validated_data.get('tracker', instance.tracker)
        instance.pet = validated_data.get('pet', instance.pet)
        instance.save()

        # Delete old data
        instance.data.all().delete()

        # Add new data
        for item in data_items:
            TrackerEntryData.objects.create(entry=instance, **item)

        return instance
