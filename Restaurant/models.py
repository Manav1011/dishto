from django.db import models
from dishto.GlobalUtils import generate_unique_hash
from django.db.models.signals import post_save, pre_save
from django.contrib.postgres.search import SearchVectorField, SearchVector
from django.dispatch import receiver
from django.contrib.postgres.indexes import GinIndex
from .tasks import generate_menu_item_embedding_task

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
    

class CategoryImage(models.Model):
    category_name = models.CharField(max_length=100, unique=True)
    image = models.ImageField(upload_to='category_images/')

class MenuCategory(models.Model):
    name = models.CharField(max_length=100)
    outlet = models.ForeignKey('Restaurant.Outlet', on_delete=models.CASCADE)
    description = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    display_order = models.PositiveIntegerField(default=0)
    slug = models.SlugField(unique=True, null=True, blank=True)
    image = models.ForeignKey(CategoryImage, on_delete=models.DO_NOTHING, null=True, blank=True)
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
    
offer_title_choices = [
    ('discount', 'Discount'),
    ('buy_one_get_one', 'Buy One Get One')
]

offer_type_choices = [
    ('percentage', 'Percentage'),
    ('flat', 'Fixed Amount')
]

class Offers(models.Model):
    title = models.CharField(max_length=100, choices=offer_title_choices, default='discount')
    type = models.CharField(max_length=20, choices=offer_type_choices, default='flat')
    value = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    description = models.TextField(null=True, blank=True)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)    
    
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
    likes = models.PositiveIntegerField(default=0)
    special_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    offers = models.ManyToManyField('Restaurant.Offers', related_name='menu_items', blank=True)
    
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
def update_menu_item_vector_signal(sender, instance, **kwargs):
    MenuItem.objects.filter(pk=instance.pk).update(
        search_vector=SearchVector(models.F("name"), models.F("description"))
    )

@receiver(pre_save, sender=MenuItem)
def generate_menu_item_embedding_signal(sender, instance, **kwargs):
    if instance.pk:
        try:
            old = MenuItem.objects.get(pk=instance.pk)
            if old.name == instance.name and old.description == instance.description:
                return  # No change, skip updating search_vector
        except MenuItem.DoesNotExist:
            pass  # New object, proceed to update
    generate_menu_item_embedding_task.delay(name=instance.name, description=instance.description, slug=instance.slug, outlet_slug=instance.category.outlet.slug)

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