from rest_framework import serializers
from .models import Product, ARModel, BodyMeasurement, ARSession, ARTryOnResult

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'

class ARModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = ARModel
        fields = '__all__'

class BodyMeasurementSerializer(serializers.ModelSerializer):
    class Meta:
        model = BodyMeasurement
        fields = '__all__'

class ARSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ARSession
        fields = '__all__'

class ARTryOnResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = ARTryOnResult
        fields = '__all__'