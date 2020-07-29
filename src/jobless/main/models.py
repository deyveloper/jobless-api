from django.db import models
from django.contrib.auth.models import User

import json


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    account = models.DecimalField(default=0, max_digits=5, decimal_places=2)
    img = models.ImageField(upload_to='UserImages')
    rating = models.IntegerField(default=0)


class Subcategory(models.Model):
    title = models.CharField(max_length=255)
    postings = models.IntegerField(default=0)


class Category(models.Model):
    title = models.CharField(max_length=255)
    postings = models.IntegerField(default=0)
    subcategories = models.ManyToManyField(Subcategory, blank=True)


class Post(models.Model):
    owner = models.ForeignKey(Profile, on_delete=models.CASCADE)
    monthprice = models.IntegerField()
    title = models.CharField(max_length=255)
    description = models.TextField()
    views = models.IntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField()
    category_json = models.TextField(
        default='{"category": null, "subcategory": null}')

    def category(self):
        categoriesjson = json.loads(self.category_json)

        try:
            category = str(Category.objects.get(pk=int(categoriesjson['category'])
                                                ).title)
            subcategory = str(Subcategory.objects.get(
                pk=int(categoriesjson['subcategory'])).title)

            return f'{category}, {subcategory}'
        except:
            return str('Այլ, այլ')


class Transaction(models.Model):
    owner = models.ForeignKey(Profile, on_delete=models.SET_NULL, null=True)
    title = models.CharField(max_length=255)
    account = models.DecimalField(default=0, max_digits=5, decimal_places=2)
    ACC_STS_CHOICE = [
        ('+', 'Ավելացում'),
        ('-', 'Պակասեցում'),
    ]
    acc_sts = models.CharField(max_length=1, choices=ACC_STS_CHOICE)
    STATUS_CHOICE = [
        ('p', 'Մշակում'),
        ('s', 'Հաջող'),
        ('r', 'Ձախողված'),
    ]
    status = models.CharField(
        max_length=1, default='p', choices=STATUS_CHOICE, )
    success = models.BooleanField(default=False)
    paymentid = models.CharField(max_length=255, blank=True)


class Urgent(models.Model):
    owner_post = models.ForeignKey(Post, on_delete=models.CASCADE)
    transaction = models.ForeignKey(
        Transaction, on_delete=models.SET_NULL, null=True)
    is_active = models.BooleanField(default=True)
    created_time = models.DateTimeField()
    end_time = models.DateTimeField()


class Top(models.Model):
    owner_post = models.ForeignKey(Post, on_delete=models.CASCADE)
    transaction = models.ForeignKey(
        Transaction, on_delete=models.SET_NULL, null=True)
    is_active = models.BooleanField(default=True)
    created_time = models.DateTimeField()
    end_time = models.DateTimeField()


class General(models.Model):
    owner_post = models.ForeignKey(Post, on_delete=models.CASCADE)
    transaction = models.ForeignKey(
        Transaction, on_delete=models.SET_NULL, null=True)
    is_active = models.BooleanField(default=True)
    created_time = models.DateTimeField()
    end_time = models.DateTimeField()


class Constant(models.Model):
    key = models.CharField(max_length=255)
    value = models.TextField()
    description = models.TextField(blank=True)