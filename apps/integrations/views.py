from rest_framework import generics
from .models import Integration, WhatsAppIntegration, EcommerceIntegration, IntegrationLog
from .serializers import IntegrationSerializer, WhatsAppIntegrationSerializer, EcommerceIntegrationSerializer, IntegrationLogSerializer

class IntegrationListView(generics.ListAPIView):
    queryset = Integration.objects.all()
    serializer_class = IntegrationSerializer

class IntegrationCreateView(generics.CreateAPIView):
    queryset = Integration.objects.all()
    serializer_class = IntegrationSerializer

class IntegrationDetailView(generics.RetrieveAPIView):
    queryset = Integration.objects.all()
    serializer_class = IntegrationSerializer

class IntegrationUpdateView(generics.UpdateAPIView):
    queryset = Integration.objects.all()
    serializer_class = IntegrationSerializer

class IntegrationDeleteView(generics.DestroyAPIView):
    queryset = Integration.objects.all()
    serializer_class = IntegrationSerializer

class IntegrationTestView(generics.GenericAPIView):
    def post(self, request, pk):
        return Response({"message": "Integration test endpoint"})

class WhatsAppIntegrationView(generics.GenericAPIView):
    def get(self, request):
        return Response({"message": "WhatsApp integration config"})

class WhatsAppSendMessageView(generics.GenericAPIView):
    def post(self, request):
        return Response({"message": "WhatsApp send message endpoint"})

class EcommerceIntegrationView(generics.GenericAPIView):
    def get(self, request):
        return Response({"message": "E-commerce integration config"})

class EcommerceSyncView(generics.GenericAPIView):
    def post(self, request):
        return Response({"message": "E-commerce sync endpoint"})

class IntegrationLogListView(generics.ListAPIView):
    queryset = IntegrationLog.objects.all()
    serializer_class = IntegrationLogSerializer
