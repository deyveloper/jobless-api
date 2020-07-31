from django.shortcuts import render
from django.db.models import Q

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from main.models import *

import json
import datetime
import decimal


class Owner(APIView):
    def get(self, request):
        if not checkOnAuth(request.user):
            resp = Response({"data": {
                "status": "failed",
                "message": "Չգրանցված."
            }}, status=status.HTTP_401_UNAUTHORIZED)
            
            return resp
        
        data = request.data

        user = request.user
        curr_user = {
            "id": user.pk,
            "profile_id": user.profile.pk,
            "info": {
                "username": user.username,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email,
                "img_url": user.profile.img.url,
            },
            "rating": str(user.profile.rating),
            "account": str(user.profile.account),
            "date_joined": str(user.date_joined),
        }
        
        resp = Response({"data": {
            "status": "success",
            "user_info": curr_user,
        }})

        return resp


class TopOwner(APIView):
    def post(self, request):
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
                "message": "ԸՆտրեք հայտարարությունը."
            }}, status=status.HTTP_400_BAD_REQUEST)

            return resp
        
        try:
            curr_post = Post.objects.get(Q(pk=postid) & Q(owner=request.user.profile))
        except:
            resp = Response({"data": {
                "status": "failed",
                "message": "Տվյալ հայտարարությունը գոյություն չունի․",
            }}, status=status.HTTP_400_BAD_REQUEST)

            return resp

        if len(curr_post.top_set.filter(is_active=True)) > 0:
            resp = Response({"data": {
                "status": "failed",
                "message": "Տվյալ հայտարարությունը արդեն գտնվում է թոփում․"
            }})

            return resp

        TOP_PRICE = int(Constant.objects.get(key="TOP_PRICE").value)
        TOP_DELAY = int(Constant.objects.get(key="TOP_DELAY").value)

        if request.user.profile.account < TOP_PRICE:
            resp = Response({"data": {
                "status": "failed",
                "message": "Ձեր հաշվին առկա գումարը բավարար չէ թոփ պիտակը գնելու համար․ Լիցքավորեք ձեր հաշիվը․",
            }})

            return resp

        now = datetime.datetime.now()
        
        other_data = {
            "title": "Top billing",
            "postid": str(postid),
            "price": str(TOP_PRICE),
            "now": str(now),
        }        

        new_tr = Transaction()
        new_tr.owner = request.user.profile
        new_tr.title = "Top"
        new_tr.account = decimal.Decimal(0) + TOP_PRICE
        new_tr.acc_sts = '-'
        new_tr.status = 's'
        new_tr.success = True
        new_tr.other_data = json.dumps(other_data)
        new_tr.save()

        minusUserAccount(request.user, TOP_PRICE)
       
        new_top = Top()
        new_top.owner_post = curr_post
        new_top.transaction = new_tr
        new_top.is_active = True
        new_top.created_time = now
        new_top.end_time = now + datetime.timedelta(seconds=TOP_DELAY)
        new_top.save()

        resp = Response({"data": {
            "status": "success",
            "message": "Հայտարարությունը հաջողությամբ տեղադրվել է թոփում․"
        }})

        return resp


class UrgentOwner(APIView):
    def post(self, request):
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
                "message": "ԸՆտրեք հայտարարությունը."
            }}, status=status.HTTP_400_BAD_REQUEST)

            return resp
        
        try:
            curr_post = Post.objects.get(Q(pk=postid) & Q(owner=request.user.profile))
        except:
            resp = Response({"data": {
                "status": "failed",
                "message": "Տվյալ հայտարարությունը գոյություն չունի․",
            }}, status=status.HTTP_400_BAD_REQUEST)

            return resp

        if len(curr_post.urgent_set.filter(is_active=True)) > 0:
            resp = Response({"data": {
                "status": "failed",
                "message": "Տվյալ հայտարարությունը արդեն ստացել է շտապ պիտակը․"
            }})

            return resp

        URGENT_PRICE = int(Constant.objects.get(key="URGENT_PRICE").value)
        URGENT_DELAY = int(Constant.objects.get(key="URGENT_DELAY").value)

        if request.user.profile.account < URGENT_PRICE:
            resp = Response({"data": {
                "status": "failed",
                "message": "Ձեր հաշվին առկա գումարը բավարար չէ շտապ պիտակը գնելու համար․ Լիցքավորեք ձեր հաշիվը․",
            }})

            return resp

        now = datetime.datetime.now()
        
        other_data = {
            "title": "Urgent billing",
            "postid": str(postid),
            "price": str(URGENT_PRICE),
            "now": str(now),
        }        

        new_tr = Transaction()
        new_tr.owner = request.user.profile
        new_tr.title = "Urgent"
        new_tr.account = decimal.Decimal(0) + URGENT_PRICE
        new_tr.acc_sts = '-'
        new_tr.status = 's'
        new_tr.success = True
        new_tr.other_data = json.dumps(other_data)
        new_tr.save()

        minusUserAccount(request.user, URGENT_PRICE)

        new_urgent = Urgent()
        new_urgent.owner_post = curr_post
        new_urgent.transaction = new_tr
        new_urgent.is_active = True
        new_urgent.created_time = now
        new_urgent.end_time = now + datetime.timedelta(seconds=URGENT_DELAY)
        new_urgent.save()

        resp = Response({"data": {
            "status": "success",
            "message": "Հայտարարությունը հաջողությամբ ստացել է շտապ պիտակը․"
        }})

        return resp


class GeneralOwner(APIView):
    def post(self, request):
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
                "message": "ԸՆտրեք հայտարարությունը."
            }}, status=status.HTTP_400_BAD_REQUEST)

            return resp
        
        try:
            curr_post = Post.objects.get(Q(pk=postid) & Q(owner=request.user.profile))
        except:
            resp = Response({"data": {
                "status": "failed",
                "message": "Տվյալ հայտարարությունը գոյություն չունի․",
            }}, status=status.HTTP_400_BAD_REQUEST)

            return resp

        if len(curr_post.general_set.filter(is_active=True)) > 0:
            resp = Response({"data": {
                "status": "failed",
                "message": "Տվյալ հայտարարությունը արդեն գտնվում է գլխավոր էջում․"
            }})

            return resp

        GENERAL_PRICE = int(Constant.objects.get(key="GENERAL_PRICE").value)
        GENERAL_DELAY = int(Constant.objects.get(key="GENERAL_DELAY").value)

        if request.user.profile.account < GENERAL_PRICE:
            resp = Response({"data": {
                "status": "failed",
                "message": "Ձեր հաշվին առկա գումարը բավարար չէ գլխավոր էջ պիտակը գնելու համար․ Լիցքավորեք ձեր հաշիվը․",
            }})

            return resp

        now = datetime.datetime.now()
        
        other_data = {
            "title": "General billing",
            "postid": str(postid),
            "price": str(GENERAL_PRICE),
            "now": str(now),
        }        

        new_tr = Transaction()
        new_tr.owner = request.user.profile
        new_tr.title = "General"
        new_tr.account = decimal.Decimal(0) + GENERAL_PRICE
        new_tr.acc_sts = '-'
        new_tr.status = 's'
        new_tr.success = True
        new_tr.other_data = json.dumps(other_data)
        new_tr.save()

        minusUserAccount(request.user, GENERAL_PRICE)
       
        new_general = General()
        new_general.owner_post = curr_post
        new_general.transaction = new_tr
        new_general.is_active = True
        new_general.created_time = now
        new_general.end_time = now + datetime.timedelta(seconds=GENERAL_DELAY)
        new_general.save()

        resp = Response({"data": {
            "status": "success",
            "message": "Հայտարարությունը հաջողությամբ տեղադրվել է գլխավոր էջում․"
        }})

        return resp

class PostOwner(APIView):
    @staticmethod
    def getActionData(post):
        if len(post.top_set.filter(is_active=True)) > 0:
            curr = post.top_set.filter(is_active=True)[0]
            top = {
                "active": True,
                "pk": f"{curr.pk}",
                "created_time": f"{curr.created_time}",
                "end_time": f"{curr.end_time}",
            }
        else:
            top = {
                "active": False,
                "pk": None,
                "created_time": None,
                "end_time": None,
            }

        if len(post.general_set.filter(is_active=True)) > 0:
            curr = post.general_set.filter(is_active=True)[0]
            general = {
                "active": True,
                "pk": f"{curr.pk}",
                "created_time": f"{curr.created_time}",
                "end_time": f"{curr.end_time}",
            }
        else:
            general = {
                "active": False,
                "pk": None,
                "created_time": None,
                "end_time": None,
            }

        if len(post.urgent_set.filter(is_active=True)) > 0:
            curr = post.urgent_set.filter(is_active=True)[0]
            urgent = {
                "active": True,
                "pk": f"{curr.pk}",
                "created_time": f"{curr.created_time}",
                "end_time": f"{curr.end_time}",
            }
        else:
            urgent = {
                "active": False,
                "pk": None,
                "created_time": None,
                "end_time": None,
            }

        return (top, urgent, general)

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

            top, urgent, general = self.getActionData(post)

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
                "top": top,
                "urgent": urgent,
                "general": general,
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
                top, urgent, general = self.getActionData(post)

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
                    "top": top,
                    "urgent": urgent,
                    "general": general,
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
            curr_post = Post.objects.get(
                Q(pk=postid) & Q(owner=request.user.profile))
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

    def delete(self, request):
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
                "message": "Ընտրեք հայտարարությունը․",
            }}, status=status.HTTP_400_BAD_REQUEST)

            return resp

        try:
            post = Post.objects.get(Q(pk=postid) & Q(owner=request.user.profile))
        except:
            resp = Response({"data": {
                "status": "failed",
                "message": "Տվյալ հայտարարությունը գոյություն չունի․",
            }}, status=status.HTTP_400_BAD_REQUEST)

            return resp

        post.delete()

        resp = Response({"data": {
            "status": "failed",
            "message": "Հայտարարությունը հաջողությամբ հեռացվել է․"
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
            }}, status=status.HTTP_400_BAD_REQUEST)

            return resp

        try:
            curr_post = Post.objects.get(
                Q(pk=postid) & Q(owner=request.user.profile))
        except:
            resp = Response({"data": {
                "status": "failed",
                "message": "Տվյալ հայտարարությունը գոյություն չունի․",
            }}, status=status.HTTP_400_BAD_REQUEST)

            return resp

        now = datetime.datetime.now()
        UPDATING_DELAY = int(Constant.objects.get(key="UPDATING_DELAY").value)

        if now - curr_post.updated.replace(tzinfo=None) < datetime.timedelta(seconds=UPDATING_DELAY):
            resp = Response({"data": {
                "status": "failed",
                "message": "Տվյալ հայտարարությունը դեռևս թարմացման կարիք չունի․"
            }})

            return resp

        curr_post.updated = now
        curr_post.save()

        resp = Response({"data": {
            "status": "success",
            "message": "Հայտարարությունը թարմացվել է հաջողությամբ․",
        }})

        return resp


def checkOnAuth(user):
    return user.is_authenticated

def minusUserAccount(user, account):
    user.profile.account -= decimal.Decimal(account)
    user.profile.save()
    user.save()