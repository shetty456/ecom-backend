from rest_framework import serializers
from product.models import Product, ProductImage, Category

# Serializer for ProductImage model, to handle image data.
class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ["image_url", "is_primary"]

# Serializer for Product model, with a nested serializer for images.
class ProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)  # Include a list of images in read-only mode

    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'stock', 'created_at', 'category', 'images']

# Serializer for Category model, to handle category data.
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"
