from rest_framework import viewsets, permissions
from .models import Pitch, Booking
from .serializers import PitchSerializer, BookingSerializer

# 1. فيو الملاعب: عرض فقط (Read-Only)
class PitchViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Pitch.objects.all()
    serializer_class = PitchSerializer
    permission_classes = [permissions.AllowAny] # الكل مسموح له يشوف الملاعب


class BookingViewSet(viewsets.ModelViewSet):
    
    serializer_class =BookingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Booking.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
         serializer.save(user=self.request.user)