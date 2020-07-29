from django.shortcuts import render
from django.db.models import Q

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from main.models import *


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

    def put(self, request):

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
            categories = json.loads(data['categories'])

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
            curr_category = Category.objects.get(pk=categories['category']).pk
            try:
                curr_subcategory = Category.objects.get(
                    pk=categories['subcategory']).pk
            except:
                pass
        except:
            pass


        if not curr_subcategory in curr_category.subcategories.all() and curr_subcategory and curr_category:
            # Continue
            # Imthere
            # imhere
            pass

        categories_formatted = {
            'category': curr_category,
        }


def checkOnAuth(user):
    return user.is_authenticated
