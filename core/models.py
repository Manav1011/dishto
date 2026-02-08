from django.db import models
from django.contrib.auth import get_user_model
from dishto.GlobalUtils import generate_unique_hash
from django.db.models.signals import post_save
from django.dispatch import receiver
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
    
class Feature(models.Model):
    FEATURE_CHOICES = [
        ("menu", "Menu"),
        ("ordering", "Ordering"),
        ("inventory", "Inventory"),
    ]
    name = models.CharField(max_length=50, unique=True, choices=FEATURE_CHOICES)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    slug = models.SlugField(unique=True, null=True, blank=True)
    
    def __str__(self):
        return self.get_name_display()
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_unique_hash()
        super(Feature, self).save(*args, **kwargs)

class Outlet(TimeStampedModel):
    name = models.CharField(max_length=255)
    franchise = models.ForeignKey('core.Franchise', on_delete=models.CASCADE)
    admin = models.ForeignKey('Profile.Profile', on_delete=models.SET_NULL,null=True,blank=True)
    cover_image = models.ImageField(upload_to='outlet_cover_images/', null=True, blank=True)
    features = models.ManyToManyField(Feature, blank=True, related_name='ouetlet_features', help_text="Features enabled for this outlet")
    superadmin_approved = models.BooleanField(default=False)
    slug = models.SlugField(unique=True, null=True, blank=True)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_unique_hash()
        super(Outlet, self).save(*args, **kwargs)
    
    def __str__(self):
        return self.name
    
class OutletFeatureHistory(models.Model):
    outlet = models.ForeignKey(Outlet, on_delete=models.CASCADE, related_name='feature_history')
    features = models.ManyToManyField(Feature)
    changed_at = models.DateTimeField(auto_now_add=True)
    changed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    note = models.TextField(blank=True)

    def __str__(self):
        return f"{self.outlet.name} features at {self.changed_at}"


class OutletFeatureRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    outlet = models.ForeignKey(Outlet, on_delete=models.CASCADE, related_name='feature_requests')
    features = models.ManyToManyField(Feature)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    requested_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='feature_requests_made')
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='feature_requests_approved')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    note = models.TextField(blank=True, help_text="Reason for rejection or other notes")

    def __str__(self):
        return f"Request for {self.outlet.name} at {self.created_at}"


@receiver(post_save, sender=OutletFeatureRequest)
def process_feature_request(sender, instance, created, **kwargs):    
    if not created and instance.status == 'approved':        
        # Update the Outlet's features based on the approved request
        current_outlet_features = instance.outlet.features.all()
        requested_features = instance.features.all()

        # Remove features that are no longer requested
        for feature in current_outlet_features:
            if feature not in requested_features:
                instance.outlet.features.remove(feature)
        
        # Add newly requested features
        for feature in requested_features:
            if feature not in current_outlet_features:
                instance.outlet.features.add(feature)
        
        # Create an OutletFeatureHistory record for the approved change
        history_entry = instance.outlet.feature_history.create(
            changed_by=instance.approved_by if instance.approved_by else instance.requested_by,
            note=f"Features updated via request #{instance.id} (Approved by {instance.approved_by if instance.approved_by else 'System'})"
        )
        history_entry.features.set(requested_features)




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
    