from django.db import models
from django.contrib.auth.models import User

import json


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    account = models.DecimalField(default=0, max_digits=20, decimal_places=2)
    img = models.ImageField(upload_to='UserImages/', default="default.png")
    rating = models.IntegerField(default=0)


class Category(models.Model):
    title = models.CharField(max_length=255)
    naming = models.CharField(max_length=255)


class Post(models.Model):
    owner = models.ForeignKey(Profile, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    monthprice = models.IntegerField()
    title = models.CharField(max_length=255)
    description = models.TextField()
    views = models.IntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField()

    def is_top(self, ):
        return len(self.top_set.filter(is_active=True)) > 0

    def is_urgent(self, ):
        return len(self.urgent_set.filter(is_active=True)) > 0
    
    def is_general(self, ):
        return len(self.general_set.filter(is_active=True)) > 0

class Transaction(models.Model):
    owner = models.ForeignKey(Profile, on_delete=models.SET_NULL, null=True)
    title = models.CharField(max_length=255)
    account = models.DecimalField(default=0, max_digits=20, decimal_places=2)
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
    other_data = models.TextField(blank=True)
    created_time = models.DateTimeField(auto_now_add=True)

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