from django.db.models.signals import post_save # الإشارة اللي بتضرب "بعد الحفظ"
from django.contrib.auth.models import User    # المرسل (Sender)
from django.dispatch import receiver          # المستقبل (Receiver) اللي بيلقط الإشارة
from .models import Profile                   # الجدول العايزين ننشئ فيه البروفايل

@receiver(post_save,sender=User)
def create_userporfile (sender, instance, created,**kwargs):
    if created:
        Profile.objects.get_or_create(user=instance)

    
@receiver(post_save,sender=User)
def save_user_profile (sender, instance,**kwargs):
    # التفاصيل المملة: الدالة دي عشان لو اليوزر مستقبلاً عدل اسمه أو إيميله، 
    # البروفايل يعمل حفظ وتحديث أوتوماتيك عشان يفضلوا متزامنين.
    instance.profile.save()
