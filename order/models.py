from django.db import models


class Order(models.Model):
    user         = models.ForeignKey('user.User', on_delete=models.CASCADE)
    created_at   = models.DateTimeField(auto_now_add=True)
    order_status = models.ForeignKey('OrderStatus', on_delete=models.CASCADE)

    class Meta:
        db_table = 'orders'


class OrderStatus(models.Model):
    status = models.CharField(max_length=800)

    class Meta:
        db_table = 'order_statuses'


class Cart(models.Model):
    user      = models.ForeignKey('user.User', related_name='carts', on_delete=models.CASCADE)
    product   = models.ForeignKey('product.Product', on_delete=models.CASCADE)
    size      = models.ForeignKey('product.Size', on_delete=models.CASCADE)
    color     = models.ForeignKey('product.Color',on_delete=models.CASCADE)
    order     = models.ForeignKey('Order', on_delete=models.CASCADE, null=True, blank=True)
    thumbnail = models.ForeignKey('product.Image', on_delete=models.CASCADE)
    quantity  = models.IntegerField(default=0)

    class Meta:
        db_table = 'carts'
