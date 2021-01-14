from django.db              import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Menu(models.Model):
    name = models.CharField(max_length=45)

    class Meta:
        db_table = "menus"


class MainCategory(models.Model):
    name  = models.CharField(max_length=45)
    menu  = models.ForeignKey('Menu', on_delete=models.CASCADE)

    class Meta:
        db_table = "main_categories"


class SubCategory(models.Model):
    name  = models.CharField(max_length=45)
    main_category  = models.ForeignKey('MainCategory', on_delete=models.CASCADE)

    class Meta:
        db_table = "sub_categories"


class Product(models.Model):
    name          = models.CharField(max_length=45)
    sub_category  = models.ForeignKey('SubCategory', on_delete=models.CASCADE)
    code          = models.CharField(max_length=45)
    price         = models.DecimalField(max_digits = 20, decimal_places = 2)
    description   = models.TextField(null=True)
    discount_rate = models.IntegerField(default=0)
    hashtags      = models.ManyToManyField('Hashtag', through ='ProductHashtag')
    sizes         = models.ManyToManyField('Size', through ='ProductSize')
    colors        = models.ManyToManyField('Color', through ='ProductColorImage')

    class Meta:
        db_table = "products"


class ProductSize(models.Model):
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    size    = models.ForeignKey('Size', on_delete=models.CASCADE)

    class Meta:
        db_table = "products_sizes"


class ProductColorImage(models.Model):
    product = models.ForeignKey('Product', related_name="productcolorimages", on_delete=models.CASCADE)
    color   = models.ForeignKey('Color', on_delete=models.CASCADE)
    image   = models.ForeignKey('Image', null= True, on_delete=models.CASCADE)

    class Meta:
        db_table = "products_colors_images"


class ProductHashtag(models.Model):
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    hashtag = models.ForeignKey('Hashtag', on_delete=models.CASCADE)

    class Meta:
        db_table = "products_hashtags"


class Size(models.Model):
    name = models.CharField(max_length=45)

    class Meta:
        db_table = "sizes"


class Color(models.Model):
    name = models.CharField(max_length=45)

    class Meta:
        db_table = "colors"


class Hashtag(models.Model):
    name = models.CharField(max_length=45)

    class Meta:
        db_table = "hashtags"


class Image(models.Model):
    image_url = models.URLField(max_length=2048)

    class Meta:
        db_table = "images"


class Review(models.Model):
    user        = models.ForeignKey('user.User', on_delete=models.CASCADE, related_name="reviews")
    product     = models.ForeignKey('Product', on_delete=models.CASCADE, related_name="reviews")
    score       = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(5)])
    description = models.TextField(null=True)
    image_url   = models.URLField(max_length=2048, null=True)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "reviews"