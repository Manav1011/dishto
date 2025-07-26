from django.db import models
from core.models import TimeStampedModel
from Restaurant.models import MenuItem
from dishto.GlobalUtils import generate_unique_hash

# Create your models here.

class Order(TimeStampedModel):
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

class OrderItem(TimeStampedModel):
    order = models.ForeignKey('Inventory.Order', on_delete=models.CASCADE)
    item = models.ForeignKey('Restaurant.MenuItem', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    inventory_transactions = models.ManyToManyField('Inventory.InventoryTransaction', blank=True, related_name='order_items', help_text="Inventory transactions related to this order item")
    slug = models.SlugField(unique=True, null=True, blank=True)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_unique_hash()
        super(OrderItem, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.quantity} x {self.item.name}"

class Ingredient(TimeStampedModel):
    UNIT_CHOICES = [
        ('kg', 'Kilogram'),
        ('g', 'Gram'),
        ('l', 'Litre'),
        ('ml', 'Millilitre'),
        ('pcs', 'Pieces'),
        ('tbsp', 'Tablespoon'),
        ('tsp', 'Teaspoon'),
        ('oz', 'Ounce'),
        ('lb', 'Pound'),
    ]
    name = models.CharField(max_length=100)
    unit = models.CharField(max_length=10, choices=UNIT_CHOICES)
    current_stock = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    minimum_stock = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    outlet = models.ForeignKey('Restaurant.Outlet', on_delete=models.CASCADE)
    slug = models.SlugField(unique=True, null=True, blank=True)

    class Meta:
        unique_together = ("name", "outlet")
        
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_unique_hash()
        super(Ingredient, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.current_stock} {self.unit})"

class MenuItemIngredient(models.Model):
    pk = models.CompositePrimaryKey("menu_item", "ingredient")
    menu_item = models.ForeignKey('Restaurant.MenuItem', on_delete=models.CASCADE, related_name='ingredients')
    ingredient = models.ForeignKey('Inventory.Ingredient', on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, help_text="Amount of ingredient per menu item")
    slug = models.SlugField(unique=True, null=True, blank=True)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_unique_hash()
        super(MenuItemIngredient, self).save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.menu_item.name} - {self.ingredient.name} ({self.quantity})"

class InventoryTransaction(TimeStampedModel):
    """
    InventoryTransaction tracks all stock changes for ingredients.

    Transaction types:
    - purchase: Stock added to inventory (e.g., buying new ingredients).
    - usage: Stock deducted due to menu item sales or kitchen use.
    - wastage: Stock lost due to spoilage, damage, or expiration.
    - adjustment: Manual correction of stock (e.g., inventory count corrections).
    """
    TRANSACTION_TYPES = (
        ('purchase', 'Purchase'),
        ('usage', 'Usage'),
        ('wastage', 'Wastage'),
        ('adjustment', 'Adjustment'),
    )
    ingredient = models.ForeignKey('Inventory.Ingredient', on_delete=models.CASCADE)
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    note = models.TextField(null=True, blank=True)
    outlet = models.ForeignKey('Restaurant.Outlet', on_delete=models.CASCADE)
    slug = models.SlugField(unique=True, null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_unique_hash()
        super(InventoryTransaction, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.transaction_type} - {self.ingredient.name} ({self.quantity})"