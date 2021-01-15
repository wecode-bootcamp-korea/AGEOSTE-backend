import os
import django
import csv

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ageoste.settings")
django.setup()

from product.models import *
from user.models import *

def DeleteData():
    Review.objects.all().delete()
    Color.objects.all().delete()
    Size.objects.all().delete()
    Hashtag.objects.all().delete()
    User.objects.all().delete()
    Menu.objects.all().delete()
    MainCategory.objects.all().delete()
    SubCategory.objects.all().delete()
    Product.objects.all().delete()
    ProductSize.objects.all().delete()
    ProductHashtag.objects.all().delete()
    Color.objects.all().delete()
    Image.objects.all().delete()
    Review.objects.all().delete()

DeleteData()

COLOR = ['R','G','B','W']
for i in COLOR:
    Color.objects.create(name=i)

for i in range(1,10):
    color_name = 'color' + str(i)
    Color.objects.create(name=color_name)

for i in range(1,6):
    size_name = 'size' + str(i)
    Size.objects.create(name=size_name)

for i in range(1,10):
    hashtag_name = 'hashtag' + str(i)
    Hashtag.objects.create(name=hashtag_name)


u = User.objects.create(
    name='이름1',
    email='1234@naver.com',
    phone_number='1234',
    password=12341234,
)

CSV_PATH_PRODUCTS = 'product.csv'

with open(CSV_PATH_PRODUCTS) as in_file:
    data_reader = csv.reader(in_file)
    #next(data_reader,None)
    for row in data_reader:
        if 'END' in row:
            break

        if row [0]:
            menu_name = row[0]
            Menu.objects.create(name = menu_name)

        if row[1]:
            maincategory_name = row[1]
            menu = Menu.objects.get(name = menu_name)
            MainCategory.objects.create(name = maincategory_name, menu = menu)

        if row[2]:
            subcategory_name = row[2]
            maincategory = MainCategory.objects.get(name = maincategory_name)
            SubCategory.objects.create(name = subcategory_name, main_category = maincategory)

        if row[3]:
            product_infoes = row[3].split('-')

            subcategory = SubCategory.objects.get(name = subcategory_name)
            product = Product.objects.create(
                name          = product_infoes[0],
                code          = product_infoes[1],
                price         = product_infoes[2],
                description   = product_infoes[3],
                discount_rate = product_infoes[4],
                sub_category  = subcategory
            )

            sizes = row[4].split('-') 
            for size in sizes:
                size = Size.objects.get(name=size)
                ProductSize.objects.create(product=product,size=size)

            hashtags = row[5].split('-') 
            for hashtag in hashtags:
                hashtag = Hashtag.objects.get(name=hashtag)
                ProductHashtag.objects.create(product=product,hashtag=hashtag)

            colores = row[6].split('-') 
            for color in colores:
                color = Color.objects.get(name=color)

                for i in range(4):
                    image_url = product.name + color.name + 'image' + str(i)
                    image = Image.objects.create(image_url = image_url)
                    ProductColorImage.objects.create(product=product,color=color,image=image)

            for i in range(3):
                score       = i
                description = product.name + 'review 내용' + str(i)
                image_url   = product.name + 'review image' + str(i)
                Review.objects.create(
                    product = product,
                    user = u,
                    score = score,
                    description = description,
                    image_url = image_url
                )





print("==========================================END========================================")
