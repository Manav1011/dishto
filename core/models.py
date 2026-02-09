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
    
class GlobalFeature(models.Model):
    """
    Master list of all available features in the system (e.g., Menu, Ordering).
    This is the single source of truth for what features exist.
    """
    FEATURE_CHOICES = [
        ("menu", "Menu"),
        ("ordering", "Ordering"),
        ("inventory", "Inventory"),
    ]
    name = models.CharField(max_length=50, unique=True, choices=FEATURE_CHOICES)
    slug = models.SlugField(unique=True, null=True, blank=True)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return self.get_name_display()

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self.name
        super(GlobalFeature, self).save(*args, **kwargs)

class OutletFeature(models.Model):
    """
    Represents an active feature subscription for a specific outlet,
    including the custom price for that subscription.
    """
    outlet = models.ForeignKey('Outlet', on_delete=models.CASCADE)
    global_feature = models.ForeignKey(GlobalFeature, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    class Meta:
        unique_together = ('outlet', 'global_feature') # An outlet can only have one subscription per global feature

    def __str__(self):
        return f"{self.outlet.name} - {self.global_feature.name} Subscription"

class Outlet(TimeStampedModel):
    name = models.CharField(max_length=255)
    franchise = models.ForeignKey('core.Franchise', on_delete=models.CASCADE)
    admin = models.ForeignKey('Profile.Profile', on_delete=models.SET_NULL,null=True,blank=True)
    cover_image = models.ImageField(upload_to='outlet_cover_images/', null=True, blank=True)
    features = models.ManyToManyField(GlobalFeature, through=OutletFeature, related_name='outlets_with_feature')
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
    features = models.ManyToManyField(GlobalFeature)
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
    REQUEST_TYPE_CHOICES = [
        ('add', 'Add Feature'),
        ('remove', 'Remove Feature'),
    ]
    outlet = models.ForeignKey(Outlet, on_delete=models.CASCADE, related_name='feature_requests')
    features = models.ManyToManyField(GlobalFeature)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    request_type = models.CharField(max_length=10, choices=REQUEST_TYPE_CHOICES, default='add')
    requested_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='feature_requests_made')
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='feature_requests_approved')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    note = models.TextField(blank=True, help_text="Reason for rejection or other notes")

    def __str__(self):
        return f"Request for {self.outlet.name} at {self.created_at}"


@receiver(post_save, sender=OutletFeatureRequest)
def process_feature_request(sender, instance, created, **kwargs):
    """
    Signal to process approved feature requests.
    Creates or deletes OutletFeature subscriptions.
    """
    if not created and instance.status == 'approved':
        outlet = instance.outlet
        requested_global_features = instance.features.all()

        if instance.request_type == 'add':
            for global_feature in requested_global_features:
                OutletFeature.objects.get_or_create(
                    outlet=outlet,
                    global_feature=global_feature,
                    defaults={'price': 0.00}
                )

        elif instance.request_type == 'remove':
            for global_feature in requested_global_features:
                OutletFeature.objects.filter(
                    outlet=outlet,
                    global_feature=global_feature
                ).delete()

        # --- Create a snapshot in OutletFeatureHistory after processing ---
        # Get the current set of active features for the outlet
        active_features = GlobalFeature.objects.filter(
            outletfeature__outlet=outlet
        )
        # Create the history record
        history = OutletFeatureHistory.objects.create(
            outlet=outlet,
            changed_by=instance.approved_by,
            note=instance.note or f"Request {instance.id} {instance.request_type} approved"
        )
        history.features.set(active_features)
        history.save()


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
    