from django.shortcuts import render
from django.db.models import Q

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from main.models import *

import random
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
            "rating": user.profile.rating,
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
            curr_post = Post.objects.get(
                Q(pk=postid) & Q(owner=request.user.profile))
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
            curr_post = Post.objects.get(
                Q(pk=postid) & Q(owner=request.user.profile))
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
            curr_post = Post.objects.get(
                Q(pk=postid) & Q(owner=request.user.profile))
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
                'category': getCategoryJson(post.category),
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
            posts = Post.objects.filter(
                owner=request.user.profile).order_by('-created')

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
                    'category': getCategoryJson(post.category),
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
                monthprice = int(data['monthprice'])
            except:
                monthprice = 0

            title = data['title']
            description = data['description']
            categoryid = data['categoryid']

        except:
            resp = Response({"data": {
                "status": "failed",
                "message": "Լրացրեք բոլոր պահանջվող տվյալները․",
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
                "message": "Նկարագրությունը պետք է բաղկացած լինի ամենաքիչը 50 սիմվոլներից․"
            }}, status=status.HTTP_400_BAD_REQUEST)

            return resp

        try:
            curr_category = Category.objects.get(pk=categoryid)
        except:
            resp = Response({"data": {
                "status": "failed",
                "message": "Սխալ կատեգորիա․"
            }}, status=status.HTTP_400_BAD_REQUEST)

            return resp

        new_post = Post()
        new_post.owner = request.user.profile
        new_post.monthprice = monthprice
        new_post.title = title
        new_post.description = description
        new_post.category = curr_category
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
            categoryid = int(data['categoryid'])
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

        try:
            curr_category = Category.objects.get(pk=categoryid)
        except:
            resp = Response({"data": {
                "status": "failed",
                "message": "Սխալ կատեգորիա․",
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

        curr_post.title = title
        curr_post.description = description
        curr_post.monthprice = monthprice
        curr_post.category = curr_category
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
            post = Post.objects.get(
                Q(pk=postid) & Q(owner=request.user.profile))
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


class OtherUser(APIView):
    def get(self, request):
        if not checkOnAuth(request.user):
            resp = Response({"data": {
                "status": "failed",
                "message": "Չգրանցված."
            }}, status=status.HTTP_401_UNAUTHORIZED)

            return resp

        data = request.GET

        allposts = False
        try:
            allposts = "true" == data['allposts'].lower()
        except:
            pass

        try:
            userid = data['userid']
        except:
            resp = Response({"data": {
                "status": "failed",
                "message": "Նշեք օգտատիրոջը․",
            }}, status=status.HTTP_400_BAD_REQUEST)

            return resp

        try:
            curr_user = User.objects.get(Q(pk=userid) & Q(is_active=True))
        except:
            resp = Response({"data": {
                "status": "failed",
                "message": "Տվյալ օգտատերը գոյություն չունի․",
            }}, status=status.HTTP_400_BAD_REQUEST)

            return resp

        user_json = getOtherUserJson(curr_user)

        if allposts:
            allposts_qs = curr_user.profile.post_set.all()

            allposts_json = []

            for post in allposts_qs:
                curr_post = getOtherPostJson(post)

                allposts_json.append(curr_post)

            user_json['posts'] = allposts_json

        resp = Response({"data": {
            "status": "success",
            "user_info": user_json
        }})

        return resp


class OtherPost(APIView):
    def get(self, request):
        if not checkOnAuth(request.user):
            resp = Response({"data": {
                "status": "failed",
                "message": "Չգրանցված."
            }}, status=status.HTTP_401_UNAUTHORIZED)

            return resp

        data = request.GET

        try:
            postid = data['postid']
        except:
            resp = Response({"data": {
                "status": "failed",
                "message": "Նշեք հայտարարությունը․",
            }}, status=status.HTTP_400_BAD_REQUEST)

            return resp

        try:
            curr_post = Post.objects.get(
                Q(pk=postid) & Q(owner__user__is_active=True))
        except:
            resp = Response({"data": {
                "status": "failed",
                "message": "Տվյալ հայտարարությունը գոյություն չունի․",
            }}, status=status.HTTP_400_BAD_REQUEST)

            return resp

        post_json = getOtherPostJson(curr_post)

        resp = Response({"data": {
            "status": "success",
            "post_info": post_json,
        }})

        return resp


class GeneralRandom(APIView):
    def get(self, request):
        if not checkOnAuth(request.user):
            resp = Response({"data": {
                "status": "failed",
                "message": "Չգրանցված."
            }}, status=status.HTTP_401_UNAUTHORIZED)

            return resp

        posts_count_arr = [5, 10, 15, 20]
        cats_count = 2
        cats_count_reserve = cats_count

        categories = Category.objects.all()

        categories_pk = []
        categories_arr = []

        while cats_count != 0:
            curr_cat = random.choice(categories)

            if curr_cat.pk in categories_pk:
                continue

            categories_pk.append(curr_cat.pk)
            categories_arr.append(
                {'category': curr_cat, 'posts_count': random.choice(posts_count_arr)})
            cats_count -= 1

        dataresp = []
        for category_dict in categories_arr:
            curr_cat_posts_not_filtered = category_dict['category'].post_set.all(
            )
            curr_cat_posts = []

            for cr_post in curr_cat_posts_not_filtered:
                if not cr_post.is_general():
                    continue

                curr_cat_posts.append(cr_post)

            curr_cat_json = getCategoryJson(category_dict['category'])
            counting = category_dict['posts_count']

            posts_pk = []
            posts_json_arr = []

            while counting != 0 and len(curr_cat_posts) - len(posts_pk) != 0 and category_dict['posts_count'] - counting < len(curr_cat_posts) - len(posts_pk):

                curr_post = random.choice(curr_cat_posts)

                if curr_post.pk in posts_pk:
                    continue

                curr_post_json = getOtherPostJson(curr_post)

                posts_json_arr.append(curr_post_json)

                counting -= 1

            post_category = {
                'category': curr_cat_json,
                'posts': posts_json_arr,
            }

            dataresp.append(post_category)

        resp = Response({"data": {
            "status": "success",
            "message": "Հաջող․",
            "general_info": dataresp
        }})

        return resp


class SimpleSearch(APIView):
    def get(self, request):
        if not checkOnAuth(request.user):
            resp = Response({"data": {
                "status": "failed",
                "message": "Չգրանցված."
            }}, status=status.HTTP_401_UNAUTHORIZED)

            return resp

        top_counts = [1, 2, 3, 4, 5]

        data = request.GET

        query = data.get('q')
        if not query:
            resp = Response({"data": {
                "status": "failed",
                "message": "Մուտքագրեք բանալի բառը/բառերը որոնելու համար."
            }}, status=status.HTTP_400_BAD_REQUEST)

            return resp

        posts = Post.objects.filter(Q(category__title__icontains=query) | Q(
            category__naming__icontains=query) | Q(title__icontains=query) | Q(description__icontains=query))

        if len(posts) == 0:
            resp = Response({"data": {
                "status": "success",
                "message": "Ձեր նշած բանալի բառերով հայտարարություն չի գտնվել․"
            }}, status=status.HTTP_204_NO_CONTENT)

            return resp

        min_monthprice = data.get('min_monthprice')
        max_monthprice = data.get('max_monthprice')

        if min_monthprice:
            posts = posts.filter(Q(monthprice__gte=int(min_monthprice)))

        if max_monthprice:
            posts = posts.filter(Q(monthprice__lte=int(max_monthprice)))

        categoryid = data.get('categoryid')
        try:
            category = Category.objects.get(pk=categoryid)
        except:
            category = None

        if category:
            posts = posts.filter(Q(category=category))

        if len(posts) == 0:
            resp = Response({"data": {
                "status": "success",
                "message": "Ձեր նշած բանալի բառերով հայտարարություն չի գտնվել․"
            }}, status=status.HTTP_204_NO_CONTENT)

            return resp

        posts = posts.order_by('-updated')

        all_top_posts = []
        posts_json = []
        for post in posts:
            curr_post_json = getOtherPostJson(post)
            if post.is_top():
                all_top_posts.append(post)

            posts_json.append(curr_post_json)

        filtered_posts = getRandomTops(
            all_top_posts, random.choice(top_counts))
        filtered_posts_json = []

        for post in filtered_posts:
            filtered_posts_json.append(getOtherPostJson(post))

        resp = Response({"data": {
            "status": "success",
            "results": {
                "posts": posts_json,
                "top_posts": filtered_posts_json,
            }}})

        return resp


class CategoryPosts(APIView):
    def get(self, request):
        if not checkOnAuth(request.user):
            resp = Response({"data": {
                "status": "failed",
                "message": "Չգրանցված."
            }}, status=status.HTTP_401_UNAUTHORIZED)

            return resp

        data = request.GET

        try:
            categoryid = int(data['categoryid'])
        except:
            resp = Response({"data": {
                "status": "failed",
                "message": "Նշեք կատեգորիան․"
            }}, status=status.HTTP_400_BAD_REQUEST)

            return resp

        try:
            category = Category.objects.get(Q(pk=categoryid))
        except:
            resp = Response({"data": {
                "status": "failed",
                "message": "Տվյալ կատեգորիան գոյոթյուն չունի․"
            }}, status=status.HTTP_400_BAD_REQUEST)

            return resp

        posts = Post.objects.filter(Q(category=category)).order_by('-updated')

        posts_json = []
        for post in posts:
            curr_post_json = getOtherPostJson(post)
            posts_json.append(curr_post_json)

        resp = Response({"data": {
            "status": "success",
            "category_id": category.pk,
            "category_posts": posts_json,
        }})

        return resp


def checkOnAuth(user):
    return user.is_authenticated


def minusUserAccount(user, account):
    user.profile.account -= decimal.Decimal(account)
    user.profile.save()
    user.save()


def getRandomTops(posts, top_counts, all_tops=True):
    if not all_tops:
        all_top_posts = []
        for post in posts:
            if post.is_top():
                all_top_posts.append(post)
        posts = all_top_posts

    posts_pk = []
    counting = top_counts
    selected_posts = []

    while counting != 0 and len(posts) - len(posts_pk) != 0 and top_counts - counting < len(posts) - len(posts_pk):
        curr_post = random.choice(posts)

        if curr_post.pk in posts_pk:
            continue

        posts_pk.append(curr_post.pk)
        selected_posts.append(curr_post)

        counting -= 1

    return selected_posts


def getCategoryJson(category):
    cat_json = {
        'pk': category.pk,
        'title': category.title,
        'naming': category.naming,
    }

    return cat_json


def getOtherUserJson(curr_user):
    user_json = {
        "id": curr_user.pk,
        "profile_id": curr_user.profile.pk,
        "info": {
            "username": curr_user.username,
            "first_name": curr_user.first_name,
            "last_name": curr_user.last_name,
            "email": curr_user.email,
            "img_url": curr_user.profile.img.url,
        },
        "posts_count": len(curr_user.profile.post_set.all()),
        "rating": curr_user.profile.rating,
        "date_joined": str(curr_user.date_joined),
    }

    return user_json


def getOtherPostJson(post):
    top, urgent, general = PostOwner.getActionData(post)

    post_json = {
        'id': post.pk,
        'owner': {
            'id': post.owner.pk,
            'username': f'{post.owner.user.username}',
            'first_name': f'{post.owner.user.first_name}',
            'last_name': f'{post.owner.user.last_name}',
            'rating': post.owner.rating,
        },
        'title': f'{post.title}',
        'description': f'{post.description}',
        'monthprice': f'{post.monthprice}',
        'category': getCategoryJson(post.category),
        "top": top,
        "urgent": urgent,
        "general": general,
        'created': f'{post.created}',
        'updated': f'{post.updated}',
    }

    return post_json
