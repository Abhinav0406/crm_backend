from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from rest_framework.views import APIView
from django.db.models import Sum, Count, Q, F
from django.utils import timezone
from datetime import timedelta

from .models import Product, Category, ProductVariant
from .serializers import ProductSerializer, ProductListSerializer, ProductDetailSerializer, CategorySerializer, ProductVariantSerializer
from apps.users.permissions import IsRoleAllowed


class CustomProductPagination(PageNumberPagination):
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 200


class ProductListView(generics.ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductListSerializer
    permission_classes = [IsAuthenticated, IsRoleAllowed.for_roles(['business_admin', 'manager', 'inhouse_sales', 'tele_calling', 'marketing'])]
    pagination_class = CustomProductPagination
    
    def get_queryset(self):
        queryset = Product.objects.filter(tenant=self.request.user.tenant)
        
        # Filter by status
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filter by category
        category_id = self.request.query_params.get('category')
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        
        # Search by name or SKU
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | Q(sku__icontains=search)
            )
        
        # Filter by stock level
        stock_filter = self.request.query_params.get('stock')
        if stock_filter == 'low':
            queryset = queryset.filter(quantity__lte=F('min_quantity'))
        elif stock_filter == 'out':
            queryset = queryset.filter(quantity=0)
        
        return queryset.order_by('-created_at')


class ProductCreateView(generics.CreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated, IsRoleAllowed.for_roles(['business_admin', 'manager'])]
    
    def perform_create(self, serializer):
        serializer.save(tenant=self.request.user.tenant)


class ProductDetailView(generics.RetrieveAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductDetailSerializer
    permission_classes = [IsAuthenticated, IsRoleAllowed.for_roles(['business_admin', 'manager', 'inhouse_sales', 'tele_calling', 'marketing'])]
    
    def get_queryset(self):
        return Product.objects.filter(tenant=self.request.user.tenant)


class ProductUpdateView(generics.UpdateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated, IsRoleAllowed.for_roles(['business_admin', 'manager'])]
    
    def get_queryset(self):
        return Product.objects.filter(tenant=self.request.user.tenant)


class ProductDeleteView(generics.DestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated, IsRoleAllowed.for_roles(['business_admin', 'manager'])]
    
    def get_queryset(self):
        return Product.objects.filter(tenant=self.request.user.tenant)


class ProductStatsView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated, IsRoleAllowed.for_roles(['business_admin', 'manager', 'inhouse_sales', 'tele_calling', 'marketing'])]
    
    def get(self, request):
        tenant = request.user.tenant
        
        # Basic stats
        total_products = Product.objects.filter(tenant=tenant).count()
        active_products = Product.objects.filter(tenant=tenant, status='active').count()
        out_of_stock = Product.objects.filter(tenant=tenant, quantity=0).count()
        low_stock = Product.objects.filter(tenant=tenant, quantity__lte=F('min_quantity')).count()
        
        # Inventory value
        total_value = Product.objects.filter(tenant=tenant).aggregate(
            total=Sum(F('quantity') * F('cost_price'))
        )['total'] or 0
        
        # Category stats
        category_count = Category.objects.filter(tenant=tenant).count()
        
        # Recent activity
        recent_products = Product.objects.filter(
            tenant=tenant,
            created_at__gte=timezone.now() - timedelta(days=30)
        ).count()
        
        return Response({
            'total_products': total_products,
            'active_products': active_products,
            'out_of_stock': out_of_stock,
            'low_stock': low_stock,
            'total_value': float(total_value),
            'category_count': category_count,
            'recent_products': recent_products,
        })


class CategoryListView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated, IsRoleAllowed.for_roles(['business_admin', 'manager', 'inhouse_sales', 'tele_calling', 'marketing'])]
    pagination_class = None  # Disable pagination for categories
    
    def get_queryset(self):
        # Temporarily return all categories for debugging
        return Category.objects.filter(tenant=self.request.user.tenant)


class CategoryCreateView(generics.CreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated, IsRoleAllowed.for_roles(['business_admin', 'manager'])]
    
    def perform_create(self, serializer):
        serializer.save(tenant=self.request.user.tenant)


class CategoryDetailView(generics.RetrieveAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated, IsRoleAllowed.for_roles(['business_admin', 'manager', 'inhouse_sales', 'tele_calling', 'marketing'])]
    
    def get_queryset(self):
        return Category.objects.filter(tenant=self.request.user.tenant)


class CategoryUpdateView(generics.UpdateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated, IsRoleAllowed.for_roles(['business_admin', 'manager'])]
    
    def get_queryset(self):
        return Category.objects.filter(tenant=self.request.user.tenant)


class CategoryDeleteView(generics.DestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated, IsRoleAllowed.for_roles(['business_admin', 'manager'])]
    
    def get_queryset(self):
        return Category.objects.filter(tenant=self.request.user.tenant)


class ProductVariantListView(generics.ListAPIView):
    queryset = ProductVariant.objects.all()
    serializer_class = ProductVariantSerializer
    permission_classes = [IsAuthenticated, IsRoleAllowed.for_roles(['business_admin', 'manager', 'inhouse_sales', 'tele_calling', 'marketing'])]
    
    def get_queryset(self):
        product_id = self.kwargs.get('product_id')
        return ProductVariant.objects.filter(
            product_id=product_id,
            product__tenant=self.request.user.tenant
        )


class ProductVariantCreateView(generics.CreateAPIView):
    queryset = ProductVariant.objects.all()
    serializer_class = ProductVariantSerializer
    permission_classes = [IsAuthenticated, IsRoleAllowed.for_roles(['business_admin', 'manager'])]
    
    def perform_create(self, serializer):
        product_id = self.kwargs.get('product_id')
        product = Product.objects.get(id=product_id, tenant=self.request.user.tenant)
        serializer.save(product=product)


class ProductVariantDetailView(generics.RetrieveAPIView):
    queryset = ProductVariant.objects.all()
    serializer_class = ProductVariantSerializer
    permission_classes = [IsAuthenticated, IsRoleAllowed.for_roles(['business_admin', 'manager', 'inhouse_sales', 'tele_calling', 'marketing'])]
    
    def get_queryset(self):
        return ProductVariant.objects.filter(product__tenant=self.request.user.tenant)


class ProductVariantUpdateView(generics.UpdateAPIView):
    queryset = ProductVariant.objects.all()
    serializer_class = ProductVariantSerializer
    permission_classes = [IsAuthenticated, IsRoleAllowed.for_roles(['business_admin', 'manager'])]
    
    def get_queryset(self):
        return ProductVariant.objects.filter(product__tenant=self.request.user.tenant)


class ProductVariantDeleteView(generics.DestroyAPIView):
    queryset = ProductVariant.objects.all()
    serializer_class = ProductVariantSerializer
    permission_classes = [IsAuthenticated, IsRoleAllowed.for_roles(['business_admin', 'manager'])]
    
    def get_queryset(self):
        return ProductVariant.objects.filter(product__tenant=self.request.user.tenant)


class CategoryDebugView(APIView):
    """Debug view to check categories for current tenant"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        tenant = request.user.tenant
        categories = Category.objects.filter(tenant=tenant)
        return Response({
            'tenant': tenant.name,
            'categories_count': categories.count(),
            'categories': list(categories.values('id', 'name', 'is_active'))
        })


class ProductsDebugView(APIView):
    """Debug view to check products for current tenant"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        tenant = request.user.tenant
        products = Product.objects.filter(tenant=tenant)
        
        # Test the serializer
        serializer = ProductListSerializer(products, many=True)
        
        return Response({
            'tenant': tenant.name,
            'products_count': products.count(),
            'products': serializer.data,
            'gold_products': list(products.filter(category__name='Gold').values('id', 'name', 'category', 'category__name'))
        })


class ProductsByCategoryView(generics.ListAPIView):
    """Get products for a specific category"""
    serializer_class = ProductListSerializer
    permission_classes = [IsAuthenticated, IsRoleAllowed.for_roles(['business_admin', 'manager', 'inhouse_sales', 'tele_calling', 'marketing'])]
    pagination_class = None  # No pagination for category products
    
    def get_queryset(self):
        category_id = self.kwargs.get('category_id')
        return Product.objects.filter(
            tenant=self.request.user.tenant,
            category_id=category_id
        ).order_by('-created_at')
