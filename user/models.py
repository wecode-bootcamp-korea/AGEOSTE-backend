from django.db              import models
from django.core.validators import MinValueValidator, MaxValueValidator


class User(models.Model):
    name       = models.CharField(max_length=45)
    email      = models.EmailField(max_length=800)
    phone      = models.CharField(max_length=800)
    birth      = models.DateField()
    password   = models.CharField(max_length=100)
    address    = models.TextField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    boutique   = models.ForeignKey('Shop', on_delete=models.SET_NULL, null=True)

    class Meta:
        db_table = 'users'


class Shop(models.Model):
    city       = models.CharField(max_length=45)
    address    = models.TextField()
    address_en = models.TextField()
    phone      = models.CharField(max_length=800)
    work_day   = models.CharField(max_length=800)

    class Meta:
        db_table = 'shops'


class Coupons(models.Model):
    name         = models.CharField(max_length=800)
    sale_percent = models.IntegerField

    class Meta:
        db_table = 'coupons'


class User_coupon(models.Model):
    user   = models.ForeignKey('User',    on_delete=models.CASCADE)
    coupon = models.ForeignKey('Coupons', on_delete=models.CASCADE)

    class Meta:
        db_table = 'user_coupons'


class Membership(models.Model):
    user        = models.ForeignKey('User', on_delete=models.CASCADE)
    name        = models.CharField(max_length=800)
    description = models.TextField(null=True)

    class Meta:
        db_table = 'memberships'


class Order(models.Model):
    user       = models.ForeignKey('User', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'orders'


class Order_status(models.Model):
    order  = models.ForeignKey('Order', on_delete=models.CASCADE)
    status = models.CharField(max_length=800)

    class Meta:
        db_table = 'order_statuses'


class Cart_item(models.Model):
    user    = models.ForeignKey('User',            on_delete=models.CASCADE)
    product = models.ForeignKey('product.Product', on_delete=models.CASCADE)
    size    = models.ForeignKey('product.Size',    on_delete=models.CASCADE)
    color   = models.ForeignKey('product.Color',   on_delete=models.CASCADE)
    order   = models.ForeignKey('Order',           on_delete=models.CASCADE)
    count   = models.IntegerField

    class Meta:
        db_table = 'cart_items'


