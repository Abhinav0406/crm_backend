from rest_framework import serializers
from .models import Product, Category, ProductVariant


class CategorySerializer(serializers.ModelSerializer):
    product_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = '__all__'
        read_only_fields = ['tenant', 'created_at', 'updated_at']
    
    def get_product_count(self, obj):
        return obj.products.count()


class ProductVariantSerializer(serializers.ModelSerializer):
    current_price = serializers.SerializerMethodField()
    is_in_stock = serializers.SerializerMethodField()
    
    class Meta:
        model = ProductVariant
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']
    
    def get_current_price(self, obj):
        return obj.current_price
    
    def get_is_in_stock(self, obj):
        return obj.is_in_stock


class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    is_in_stock = serializers.SerializerMethodField()
    is_low_stock = serializers.SerializerMethodField()
    current_price = serializers.SerializerMethodField()
    profit_margin = serializers.SerializerMethodField()
    variants = ProductVariantSerializer(many=True, read_only=True)
    variant_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = '__all__'
        read_only_fields = ['tenant', 'created_at', 'updated_at']
    
    def get_is_in_stock(self, obj):
        return obj.is_in_stock
    
    def get_is_low_stock(self, obj):
        return obj.is_low_stock
    
    def get_current_price(self, obj):
        return obj.current_price
    
    def get_profit_margin(self, obj):
        return obj.profit_margin
    
    def get_variant_count(self, obj):
        return obj.variants.count()


class ProductDetailSerializer(ProductSerializer):
    """Extended serializer for detailed product views"""
    category_details = CategorySerializer(source='category', read_only=True)
    
    class Meta(ProductSerializer.Meta):
        fields = '__all__'


class ProductListSerializer(serializers.ModelSerializer):
    """Simplified serializer for product lists"""
    category_name = serializers.CharField(source='category.name', read_only=True)
    category = serializers.PrimaryKeyRelatedField(read_only=True)
    is_in_stock = serializers.SerializerMethodField()
    current_price = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'sku', 'category', 'category_name', 'selling_price', 
            'current_price', 'quantity', 'status', 'is_in_stock', 
            'is_featured', 'is_bestseller', 'created_at'
        ]
        read_only_fields = ['tenant', 'created_at', 'updated_at']
    
    def get_is_in_stock(self, obj):
        return obj.is_in_stock
    
    def get_current_price(self, obj):
        return obj.current_price
