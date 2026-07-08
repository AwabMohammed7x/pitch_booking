from django.db import models
from django.conf import settings # 👈 استدعينا الإعدادات عشان اليوزر

# 1. جدول الملعب
class Pitch(models.Model):
    name = models.CharField(max_length=100, verbose_name="اسم الملعب")
    price_per_hour = models.DecimalField(max_digits=6, decimal_places=2, verbose_name="السعر في الساعة")
    image = models.ImageField(upload_to='pitches_images/', verbose_name="صورة الملعب")
    description = models.TextField(blank=True, null=True, verbose_name="وصف الملعب")

    def __str__(self):
        return self.name


# 2. جدول الحجوزات
class Booking(models.Model):
    # حالات الحجز (عشان ما نكتبها غلط في الكود)
    STATUS_CHOICES = (
        ('Pending', 'قيد الانتظار'),
        ('Confirmed', 'مؤكد'),
        ('Canceled', 'ملغي'),
    )

    # 👈 هنا استخدمنا الطريقة الصحيحة لربط اليوزر
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='bookings')
    
    # ربطنا الحجز بالملعب
    pitch = models.ForeignKey(Pitch, on_delete=models.CASCADE, related_name='bookings')
    
    # أهم حقلين: البداية والنهاية
    start_time = models.DateTimeField(verbose_name="وقت البداية")
    end_time = models.DateTimeField(verbose_name="وقت النهاية")
    
    total_price = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True, verbose_name="السعر الإجمالي")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending', verbose_name="حالة الحجز")

    def __str__(self):
        return f"حجز {self.user.username} لـ {self.pitch.name}"
    
class Payment(models.Model):
    choices = (
        ('Pending', 'قيد الانتظار'),
        ('Completed', 'مكتمل'),
        ('Failed', 'فشل'),
    )
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='payment')
    amount = models.DecimalField(max_digits=8, decimal_places=2, verbose_name="المبلغ")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الدفع")
    status = models.CharField(max_length=20, choices=choices, default='Pending', verbose_name="حالة الدفع")
    transaction_id = models.CharField(max_length=100, blank=True, null=True, verbose_name="رقم المعاملة")
    

    def __str__(self):
        return f"دفع {self.amount} لـ {self.booking}"