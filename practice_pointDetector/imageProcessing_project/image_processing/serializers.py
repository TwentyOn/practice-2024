from rest_framework import serializers
from .models import Image

class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = '__all__'

        def get_url(self, obj):
            request = self.context.get('request')
            photo_url = obj.fingerprint.url
            return request.build_absolute_uri(photo_url)