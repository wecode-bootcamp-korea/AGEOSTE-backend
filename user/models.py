from django.db import models


class User(models.Model):
    name          = models.CharField(max_length=45)
    email         = models.EmailField(max_length=800)
    phone_number  = models.CharField(max_length=800)
    date_of_birth = models.DateField(null=True, blank=True)
    password      = models.CharField(max_length=100)
    address       = models.CharField(max_length=1000, null=True, blank=True)
    created_at    = models.DateTimeField(auto_now_add=True)
    updated_at    = models.DateTimeField(auto_now=True)
    favorite_shop = models.ForeignKey('Shop', on_delete=models.SET_NULL, null=True, blank=True)
    membership    = models.ForeignKey('Membership', on_delete=models.CASCADE, default = 1)

    class Meta:
        db_table = 'users'


class Shop(models.Model):
    city         = models.CharField(max_length=45)
    name         = models.CharField(max_length=45)
    address      = models.CharField(max_length=1000)
    phone_number = models.CharField(max_length=800)
    work_day     = models.CharField(max_length=800)

    class Meta:
        db_table = 'shops'


class Coupon(models.Model):
    name          = models.CharField(max_length=800)
    discount_rate = models.IntegerField()

    class Meta:
        db_table = 'coupons'


class UserCoupon(models.Model):
    user   = models.ForeignKey('User', on_delete=models.CASCADE)
    coupon = models.ForeignKey('Coupon', on_delete=models.CASCADE)

    class Meta:
        db_table = 'user_coupons'


class Membership(models.Model):
    grade         = models.CharField(max_length=800)
    discount_rate = models.IntegerField(null=True)

    class Meta:
        db_table = 'memberships'


