from rest_framework import serializers
from django.utils import timezone  # 👈 مهم جداً عشان نجيب الزمن الحالي صح
from .models import Pitch, Booking, Payment

class PitchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pitch
        fields = '__all__'  # حيعرض كل حاجة (الاسم، السعر، الصورة)



class BookingSerializer(serializers.ModelSerializer):
    # بنخلي الحقول دي للقراءة فقط، لأن السيستم هو اللي حيملاها مش الزبون
    user = serializers.ReadOnlyField(source='user.username')
    total_price = serializers.ReadOnlyField()
    status = serializers.ReadOnlyField()

    class Meta:
        model = Booking
        fields = ['id', 'user', 'pitch', 'start_time', 'end_time', 'total_price', 'status']

    # 🛑 هنا حارس البوابة: دالة التحقق (Validation)
    def validate(self, data):
        start_time = data['start_time']
        end_time = data['end_time']
        pitch = data['pitch']

        # 1. الفلتر الأول (منطقية الزمن): هل النهاية قبل البداية؟
        if start_time >= end_time:
            raise serializers.ValidationError("غير منطقي: وقت النهاية يجب أن يكون بعد وقت البداية.")

        # 2. الفلتر الثاني (الزمن الماضي): هل بيحجز في الماضي؟
        if start_time < timezone.now():
            raise serializers.ValidationError("عفواً، لا يمكنك الحجز في وقت مضى.")

        # 3. الفلتر الثالث (حل التعارض): هل الملعب محجوز في نفس الزمن؟
        # اللوجيك: بنبحث في الداتا بيز عن أي حجز لنفس الملعب بيتقاطع مع الزمن الجديد
        # التقاطع بيحصل لو: بداية الحجز الجديد < نهاية حجز قديم، وفي نفس الوقت نهاية الجديد > بداية القديم
        overlapping_bookings = Booking.objects.filter(
            pitch=pitch,
            start_time__lt=end_time,
            end_time__gt=start_time
        ).exclude(status='Canceled') # بنستثني الحجوزات الملغية لأنها ما بتعمل تعارض

        if overlapping_bookings.exists():
            raise serializers.ValidationError("عفواً، هذا الملعب محجوز في هذا الوقت. يرجى اختيار وقت آخر.")

        return data # لو عدى من كل الفلاتر دي، الداتا بترجع نظيفة وجاهزة للحفظ

    # 💰 حساب السعر الإجمالي أوتوماتيك قبل الحفظ
    def create(self, validated_data):
        pitch = validated_data['pitch']
        start_time = validated_data['start_time']
        end_time = validated_data['end_time']

        # بنحسب الفرق بالساعات
        duration = end_time - start_time
        hours = duration.total_seconds() / 3600
        
        # بنضرب عدد الساعات في سعر الملعب
        total_price = float(hours) * float(pitch.price_per_hour)
        
        # بنضيف السعر الإجمالي للداتا قبل ما نحفظها
        validated_data['total_price'] = total_price
        
        # أخيراً، بنحفظ الحجز في الداتا بيز
        return super().create(validated_data)
    
class PaymentSerializer(serializers.ModelSerializer):
    booking = serializers.ReadOnlyField(source='booking.id')  # عرض بيانات الحجز المرتبط بالدفع

    class Meta:
        model = Payment
        fields = ['id', 'booking', 'amount', 'created_at', 'status', 'transaction_id']
        read_only_fields = ['created_at', 'status', 'transaction_id']  # الحقول دي للقراءة فقط 