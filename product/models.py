from django.db              import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Menu(models.Model):
    name = models.CharField(max_length=45)

    class Meta:
        db_table = "menus"


class Main_Category(models.Model):
    name    = models.CharField(max_length=45)
    menu_id = models.ForeignKey('Menu', on_delete=models.CASCADE)

    class Meta:
        db_table = "main_categories"


class Sub_Category(models.Model):
    name          = models.CharField(max_length=45)
    main_category = models.ForeignKey('Main_Category', on_delete=models.CASCADE)

    class Meta:
        db_table = "sub_categories"


class Product(models.Model):
    name         = models.CharField(max_length=45)
    sub_category = models.ForeignKey('Sub_Category', on_delete=models.CASCADE)
    code         = models.CharField(max_length=45)
    price        = models.DecimalField(max_digits = 20, decimal_places = 4)
    description  = models.TextField(null=True)
    sail_percent = models.IntegerField(default=0)
    hashtags     = models.ManyToManyField('Hashtag', through ='Product_hashtag')
    sizes        = models.ManyToManyField('Size',    through ='Product_size')
    colors       = models.ManyToManyField('Color',   through ='Product_color_image')
    images       = models.ManyToManyField('Image',   through ='Product_color_image')

    class Meta:
        db_table = "products"


class Product_size(models.Model):
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    size    = models.ForeignKey('Size',    on_delete=models.CASCADE)

    class Meta:
        db_table = "product_sizes"


class Product_color_image(models.Model):
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    color   = models.ForeignKey('Color',   on_delete=models.CASCADE)
    image   = models.ForeignKey('Image',   on_delete=models.CASCADE)

    class Meta:
        db_table = "product_color_image"


class Product_hashtag(models.Model):
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    hashtag = models.ForeignKey('Hashtag', on_delete=models.CASCADE)

    class Meta:
        db_table = "product_hashtags"


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
    user        = models.ForeignKey('User',    on_delete=models.CASCADE)
    prodct      = models.ForeignKey('Product', on_delete=models.CASCADE)
    score       = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(5)])
    created_at  = models.DateTimeField(auto_now_add=True)
    description = models.TextField(null=True)
    image_url   = models.TextField(max_length=2048, null=True)

    class Meta:
        db_table = "reviews"
