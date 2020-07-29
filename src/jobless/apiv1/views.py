from django.shortcuts import render
from django.db.models import Q

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from main.models import *

import json
import datetime


class PostOwner(APIView):
    def get(self, request):

        if not checkOnAuth(request.user):
            resp = Response({"data": {
                "status": "failed",
                "message": "Չգրանցված."
            }}, status=status.HTTP_401_UNAUTHORIZED)

            return resp

        one_post = False
        try:
            data = request.GET
            postid = int(data['postid'])
            one_post = True
        except:
            pass

        if one_post:
            try:
                post = Post.objects.get(
                    Q(pk=postid) & Q(owner=request.user.profile))
            except:
                resp = Response({"data": {
                    "status": "failed",
                    "message": "Այդ հայտարարությունը գոյություն չունի․",
                }}, status=status.HTTP_400_BAD_REQUEST)

                return resp

            dataresp = {
                'id': f'{postid}',
                'owner': {
                    'username': f'{post.owner.user.username}',
                    'first_name': f'{post.owner.user.first_name}',
                    'last_name': f'{post.owner.user.last_name}',
                },
                'title': f'{post.title}',
                'description': f'{post.description}',
                'monthprice': f'{post.monthprice}',
                'views': f'{post.views}',
                'categories': {
                    'text': post.category(),
                    'json': f'{post.category_json}',
                },
                'created': f'{post.created}',
                'updated': f'{post.updated}',
            }

            resp = Response({"data": {
                "status": "success",
                "message": "Հաջողված․",
                "post": dataresp
            }})

            return resp
        else:
            posts = Post.objects.filter(owner=request.user.profile)

            dataresp = []
            for post in posts:
                curr_data = {
                    'id': f'{post.pk}',
                    'owner': {
                        'username': f'{post.owner.user.username}',
                        'first_name': f'{post.owner.user.first_name}',
                        'last_name': f'{post.owner.user.last_name}',
                    },
                    'title': f'{post.title}',
                    'description': f'{post.description}',
                    'monthprice': f'{post.monthprice}',
                    'views': f'{post.views}',
                    'categories': {
                        'text': post.category(),
                        'json': f'{post.category_json}',
                    },
                    'created': f'{post.created}',
                    'updated': f'{post.updated}',
                }
                
                dataresp.append(curr_data)

        resp = Response({"data": {
            "status": "success",
            "message": "Հաջողված․",
            "posts": dataresp,
        }})

        return resp

    def post(self, request):

        if not checkOnAuth(request.user):
            resp = Response({"data": {
                "status": "failed",
                "message": "Չգրանցված."
            }}, status=status.HTTP_401_UNAUTHORIZED)

            return resp

        try:
            data = request.data

            owner = request.user.profile

            try:
                monthprice = data['monthprice']
            except:
                monthprice = 0

            title = data['title']
            description = data['description']
            categories = data['categories']

        except:
            resp = Response({"data": {
                "status": "failed",
                "message": "Լրացրեք բոլոր պահանջվող տվյալները․",
            }}, status=status.HTTP_400_BAD_REQUEST)

            return resp

        if len(description) < 50:
            resp = Response({"data": {
                "status": "failed",
                "message": "Նկարագրությունը պետք է բաղկացած լինի ամենաքիչը 50 սիմվոլներից․"
            }}, status=status.HTTP_400_BAD_REQUEST)

            return resp

        curr_subcategory = None
        curr_category = None

        try:
            curr_category = Category.objects.get(pk=categories['category'])
            try:
                curr_subcategory = Subcategory.objects.get(
                    pk=categories['subcategory'])
            except:
                pass
        except:
            pass
            


        if curr_subcategory and curr_category and not curr_subcategory in curr_category.subcategories.all():
            resp = Response({"data": {
                "status": "failed",
                "message": "Սխալ կատեգորիաներ․",
            }}, status=status.HTTP_400_BAD_REQUEST)

            return resp
        

        categories_formatted = {
            'category': curr_category.pk if curr_category else None,
            'subcategory': curr_subcategory.pk if curr_subcategory else None,
        }

        categories_json = json.dumps(categories_formatted)

        new_post = Post()
        new_post.owner = request.user.profile
        new_post.monthprice = monthprice
        new_post.title = title
        new_post.description = description
        new_post.category_json = categories_json
        new_post.updated = datetime.datetime.now()
        new_post.save()

        resp = Response({"data": {
            "status": "success",
            "message": "Հայտարարությունը ավելացվել է հաջողությամբ․",
        }})

        return resp

    def patch(self, request):
        if not checkOnAuth(request.user):
            resp = Response({"data": {
                "status": "failed",
                "message": "Չգրանցված."
            }}, status=status.HTTP_401_UNAUTHORIZED)

            return resp

        data = request.data

        try:
            postid = int(data['postid'])
        except:
            resp = Response({"data": {
                "status": "failed",
                "message": "Նշեք հայտարարությունը․"
            }}, status=status.HTTP_400_BAD_REQUEST)

            return resp

        try:
            title = data['title']
            description = data['description']
            monthprice = int(data['monthprice'])
            categories = data['categories']
        except:
            resp = Response({"data": {
                "status": "failed",
                "message": "Լրացրեք բոլոր տվյալները․"
            }}, status=status.HTTP_400_BAD_REQUEST)

            return resp
        
        if monthprice < 0:
            resp = Response({"data": {
                "status": "failed",
                "message": "Աշխատավարձը բացասական չի կարող լինել․"
            }})
            
            return resp

        if len(description) < 50:
            resp = Response({"data": {
                "status": "failed",
                "message": "Նկարագրությունը պետք է բաղկացած լինի ամենաքիչը 50 սիմվոլներից․",
            }}, status=status.HTTP_400_BAD_REQUEST)

            return resp

        curr_subcategory = None
        curr_category = None

        try:
            curr_category = Category.objects.get(pk=categories['category'])
            try:
                curr_subcategory = Subcategory.objects.get(
                    pk=categories['subcategory'])
            except:
                pass
        except:
            pass


        if curr_subcategory and curr_category and not curr_subcategory in curr_category.subcategories.all():
            resp = Response({"data": {
                "status": "failed",
                "message": "Սխալ կատեգորիաներ․",
            }}, status=status.HTTP_400_BAD_REQUEST)

            return resp
        

        categories_formatted = {
            'category': curr_category.pk if curr_category else None,
            'subcategory': curr_subcategory.pk if curr_subcategory else None,
        }

        categories_json = json.dumps(categories_formatted)

        
        try:
            curr_post = Post.objects.get(Q(pk=postid) & Q(owner=request.user.profile))
        except:
            resp = Response({"data": {
                "status": "failed",
                "message": "Տվյալ հայտարարությունը գոյություն չունի․",
            }}, status=status.HTTP_400_BAD_REQUEST)

            return resp

        curr_post.title = title
        curr_post.description = description
        curr_post.monthprice = monthprice
        curr_post.categories = categories_json
        curr_post.save()


        resp = Response({"data": {
            "status": "success",
            "message": "Փոփոխությունները հաջողությամբ պահպանվեցին․"
        }})

        return resp

    # Updating
    def put(self, request):
        
        if not checkOnAuth(request.user):
            resp = Response({"data": {
                "status": "failed",
                "message": "Չգրանցված."
            }}, status=status.HTTP_401_UNAUTHORIZED)

            return resp
        
        data = request.data

        try:
            postid = data['postid']    
        except:
            resp = Response({"data": {
                "status": "failed",
                "message": "Ընտրեք հայտարարությունը․"
            }})

            return resp
        
        
        try:
            curr_post = Post.objects.get(Q(pk=postid) & Q(owner=request.user.profile)) 
        except:
            resp = Response({"data": {
                "status": "failed",
                "message": "Տվյալ հայտարարությունը գոյություն չունի․",
            }}, status=status.HTTP_400_BAD_REQUEST)

            return resp
        
        now = datetime.datetime.now()
        UPDATING_DELAY = int(Constant.objects(key="UPDATING_DELAY").value)

        if now - curr_post.updated < datetime.timedelta(seconds=UPDATING_DELAY):
            resp = Response({"data": {
                "status": "failed",
                "message": "Տվյալ հայտարարությունը դեռևս թարմացման կարիք չունի"
            }})

            return resp
        
        # imthere




def checkOnAuth(user):
    return user.is_authenticated
