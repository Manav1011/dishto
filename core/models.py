from django.db import models
from django.contrib.auth import get_user_model
from dishto.GlobalUtils import generate_unique_hash
# Create your models here.


User = get_user_model()


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        
class Franchise(TimeStampedModel):
    name = models.CharField(max_length=255)
    admin = models.ForeignKey('Profile.Profile', on_delete=models.SET_NULL,null=True,blank=True)
    subdomain = models.CharField(max_length=100, unique=True, null=True, blank=True)
    slug = models.SlugField(unique=True, null=True, blank=True)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_unique_hash()
        super(Franchise, self).save(*args, **kwargs)
    
    def __str__(self):
        return self.name

class Outlet(TimeStampedModel):
    name = models.CharField(max_length=255)
    franchise = models.ForeignKey('core.Franchise', on_delete=models.CASCADE)
    admin = models.ForeignKey('Profile.Profile', on_delete=models.SET_NULL,null=True,blank=True)
    slug = models.SlugField(unique=True, null=True, blank=True)
    cover_image = models.ImageField(upload_to='outlet_cover_images/', null=True, blank=True)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_unique_hash()
        super(Outlet, self).save(*args, **kwargs)
    
    def __str__(self):
        return self.name

class OutletSliderImage(TimeStampedModel):
    outlet = models.ForeignKey('core.Outlet', on_delete=models.CASCADE, related_name='slider_images')
    image = models.ImageField(upload_to='outlet_slider_images/')
    order = models.PositiveIntegerField(default=0)
    slug = models.SlugField(unique=True, null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_unique_hash()
        super(OutletSliderImage, self).save(*args, **kwargs)

    def __str__(self):
        return self.image.name if self.image else str(self.pk)
    