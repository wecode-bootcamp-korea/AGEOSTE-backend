import json
import bcrypt
import jwt

from django.test import TestCase, Client

from my_settings import SECRET
from user.models     import User, Membership, Coupon, UserCoupon # membership default = 1

client = Client()

class SignUpViewTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        Membership.objects.create(
            id = 1,
            grade = 'test_membership',
            discount_rate = 10
        )

        Coupon.objects.create(
            id = 1,
            name = 'test_coupon',
            discount_rate = 10,
            description = 'test_coupon'
        )

        User.objects.create(
            name = 'test',
            email = 'test@wecode.com',
            password = 'test1234!',
            phone_number = '01012341234'
        )

    def tearDown(self):
        User.objects.all().delete()
        Membership.objects.all().delete()
        Coupon.objects.all().delete()

    def test_signup_success(self):
        data = {
            "name" : "test1",
            "email" : "test1@wecode.com",
            "password" : "test1234!",
            "phone_number" : "01011111111"
        }

        response = client.post('/user/signup', json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json(), {"message": "SUCCESS"})

    def test_key_error(self):
        data = {
            "email" : 'test@wecode.com',
            "password" : 'test1234!',
            "phone_number" : '01012341234'
        }

        response = client.post('/user/signup', json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"error": "KEY_ERROR"})

    def test_invalid_email(self):
        data = {
            "name" : "test",
            "email" : "testwecode.com",
            "password" : 'test1234!',
            "phone_number" : "01012341234"
        }

        response = client.post('/user/signup', json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"error": "INVALID_EMAIL"})

    def test_invalid_password(self):
        data = {
            "name" : "test",
            "email" : "test@wecode.com",
            "password" : 'test123',
            "phone_number" : "01012341234"
        }

        response = client.post('/user/signup', json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"error": "INVALID_PASSWORD"})   

    def test_invalid_phonenumber(self):
        data = {
            "name" : "test",
            "email" : "test@wecode.com",
            "password" : 'test1234!',
            "phone_number" : "0101234"
        }

        response = client.post('/user/signup', json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"error": "INVALID_PHONE_NUMBER"})

    def test_exist_email(self):
        data = {
            "name" : "test",
            "email" : "test@wecode.com",
            "password" : 'test1234!',
            "phone_number" : "01012341234"
        }

        response = client.post('/user/signup', json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"error": "EXIST_EMAIL"})

    def test_exist_phonenumber(self):
        data = {
            "name" : "test",
            "email" : "test1@wecode.com",
            "password" : 'test1234!',
            "phone_number" : "01012341234"
        }

        response = client.post('/user/signup', json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"error": "EXIST_PHONE_NUMBER"})

    def test_invalid_birth(self):
        data = {
            "name" : "test",
            "email" : "test1@wecode.com",
            "password" : 'test1234!',
            "phone_number" : "01012341233",
            "date_of_birth" : "012345"
        }

        response = client.post('/user/signup', json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"error": "INVALID_BIRTH"})