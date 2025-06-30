from django.db import models
from dishto.GlobalUtils import generate_unique_hash
from django.db.models.signals import post_save
from django.contrib.postgres.search import SearchVectorField, SearchVector
from django.dispatch import receiver
from django.contrib.postgres.indexes import GinIndex


# Create your models here.

class Franchise(models.Model):
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

class Outlet(models.Model):
    name = models.CharField(max_length=255)
    franchise = models.ForeignKey('Restaurant.Franchise', on_delete=models.CASCADE)
    admin = models.ForeignKey('Profile.Profile', on_delete=models.SET_NULL,null=True,blank=True)
    slug = models.SlugField(unique=True, null=True, blank=True)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_unique_hash()
        super(Outlet, self).save(*args, **kwargs)
    
    def __str__(self):
        return self.name

class MenuCategory(models.Model):
    name = models.CharField(max_length=100)
    outlet = models.ForeignKey('Restaurant.Outlet', on_delete=models.CASCADE)
    description = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    display_order = models.PositiveIntegerField(default=0)
    slug = models.SlugField(unique=True, null=True, blank=True)
    
    search_vector = SearchVectorField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_unique_hash()
        super(MenuCategory, self).save(*args, **kwargs)
    
    def __str__(self):
        return self.name
    
    class Meta:
        indexes = [
            GinIndex(fields=["search_vector"])  # ✅ GIN index for fast search
        ]

@receiver(post_save, sender=MenuCategory)
def update_menu_category_vector(sender, instance, **kwargs):
    MenuCategory.objects.filter(pk=instance.pk).update(
        search_vector=SearchVector(models.F("name"), models.F("description"))
    )

class MenuItem(models.Model):
    name = models.CharField(max_length=100)
    category = models.ForeignKey('Restaurant.MenuCategory', on_delete=models.CASCADE)
    description = models.TextField(null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    is_available = models.BooleanField(default=True)
    image = models.ImageField(upload_to='menu_items/', null=True, blank=True)
    display_order = models.PositiveIntegerField(default=0)
    slug = models.SlugField(unique=True, null=True, blank=True)
    
    search_vector = SearchVectorField(blank=True, null=True)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_unique_hash()
        super(MenuItem, self).save(*args, **kwargs)
    
    def __str__(self):
        return self.name
    
    class Meta:
        indexes = [
            GinIndex(fields=["search_vector"])  # ✅ GIN index for fast search
        ]
        
@receiver(post_save, sender=MenuItem)
def update_menu_item_vector(sender, instance, **kwargs):
    MenuItem.objects.filter(pk=instance.pk).update(
        search_vector=SearchVector(models.F("name"), models.F("description"))
    )

class Order(models.Model):
    ORDER_STATUS = (
        ('pending', 'Pending'),
        ('preparing', 'Preparing'),
        ('ready', 'Ready'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled')
    )
    
    outlet = models.ForeignKey('Restaurant.Outlet', on_delete=models.CASCADE)    
    order_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=ORDER_STATUS, default='pending')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    special_instructions = models.TextField(null=True, blank=True)
    slug = models.SlugField(unique=True, null=True, blank=True)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_unique_hash()
        super(Order, self).save(*args, **kwargs)
    
    def __str__(self):
        return f"Order #{self.id} - {self.customer}"

class OrderItem(models.Model):
    order = models.ForeignKey('Restaurant.Order', on_delete=models.CASCADE)
    item = models.ForeignKey('Restaurant.MenuItem', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return f"{self.quantity} x {self.item.name}"