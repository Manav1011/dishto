from django.db import models
from core.models import TimeStampedModel
from Menu.models import MenuItem
from dishto.GlobalUtils import generate_unique_hash
from django.db.models.signals import post_save
from django.dispatch import receiver
from decimal import Decimal

# Create your models here.


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
    outlet = models.ForeignKey('core.Outlet', on_delete=models.CASCADE)
    slug = models.SlugField(unique=True, null=True, blank=True)

    class Meta:
        unique_together = ("name", "outlet")
        
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_unique_hash()
        super(Ingredient, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.current_stock} {self.unit})"

class MenuItemIngredient(TimeStampedModel):
    pk = models.CompositePrimaryKey("menu_item", "ingredient")
    menu_item = models.ForeignKey('Menu.MenuItem', on_delete=models.CASCADE, related_name='ingredients')
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
    outlet = models.ForeignKey('core.Outlet', on_delete=models.CASCADE)
    slug = models.SlugField(unique=True, null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_unique_hash()
        super(InventoryTransaction, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.transaction_type} - {self.ingredient.name} ({self.quantity})"

@receiver(post_save, sender=InventoryTransaction)
def update_ingredient_stock(sender, instance, created, **kwargs):    
    ingredient = instance.ingredient
    qty = instance.quantity if isinstance(instance.quantity, Decimal) else Decimal(str(instance.quantity))
    if instance.transaction_type == 'purchase':
        ingredient.current_stock = ingredient.current_stock + qty
    elif instance.transaction_type in ['usage', 'wastage']:
        new_stock = ingredient.current_stock - qty
        if new_stock < 0:
            raise ValueError(f"Stock for ingredient '{ingredient.name}' cannot go negative. Current: {ingredient.current_stock}, Tried to reduce by: {qty}")
        ingredient.current_stock = new_stock
    elif instance.transaction_type == 'adjustment':
        if qty < 0:
            raise ValueError(f"Stock for ingredient '{ingredient.name}' cannot be set to negative value: {qty}")
        ingredient.current_stock = qty
    ingredient.save()
