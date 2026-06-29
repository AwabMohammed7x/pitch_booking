from django.db import models
from django.contrib.auth.models import User
# Create your models here.
class Profile(models.Model):
    # 🦸‍♂️ المنقذ: إضافة related_name عشان السيريالايزر يربطهم صح
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    
    bio = models.TextField(max_length=500, blank=True)
    phone_number = models.CharField(max_length=15, blank=True)
    profile_pic = models.ImageField(upload_to='profile_pics/', default='default.jpg', blank=True)

    def __str__(self):
        return f"بروفايل المستخدم: {self.user.username}"
    
