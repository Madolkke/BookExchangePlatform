from django.shortcuts import render

from django.http import HttpResponse, JsonResponse

import bep
from bep.models import BepUser, Session, Book, Order
from django.core.paginator import Paginator
import django.utils.datastructures
import json


# Create your views here.

def login_page(request):
    return render(request, 'login.html')


def register_page(request):
    return render(request, 'register.html')


def personal_info_page(request):
    return render(request, 'personal_info.html')


def create_book_page(request):
    return render(request, 'create_book.html')


def index_page(request, page_number):
    book_list = bep.models.Book.objects.all()
    paginator = Paginator(book_list, 12)
    books = paginator.get_page(page_number)
    mid = []
    for book in books:
        if not book.is_sold:
            mid.append(book)
    context = {
        "page_number": page_number,
        "books": mid,
        "has_next": books.has_next(),
        "has_previous": books.has_previous(),
        "next_page_number": page_number + 1,
        "previous_page_number": page_number - 1,
    }
    return render(request, 'index.html', context)


def order_list_page(request, session_str):
    bep_user_id = Session.check_session(session_str)
    user = BepUser.objects.get(id=bep_user_id)
    order_list = Order.objects.filter(purchaser_id=user.id)
    orders = []
    for order in order_list:
        mid = {"id": order.id}
        if order.deprecated:
            mid["status"] = "已终止"
            mid["visible"] = False
        elif order.finished:
            mid["status"] = "已完成"
            mid["visible"] = False
        else:
            mid["status"] = "已支付"
            mid["visible"] = True
        book = Book.objects.get(id=order.book_id)
        mid["name"] = book.name
        mid["img"] = book.cover
        mid["date"] = order.pub_time
        orders.append(mid)
    context = {
        "orders": orders
    }
    return render(request, 'order_list.html', context)


def book_detail(request, book_id):
    book = bep.models.Book.objects.get(id=book_id)
    if book.is_need:
        book_type = "需求"
    else:
        book_type = "出售"
    context = {
        "book": book,
        "type": book_type
    }
    return render(request, 'detail.html', context)


def login_validation(request):
    json_request = json.loads(request.body)
    account = json_request['account']
    password = json_request['password']
    try:
        bu = BepUser.objects.get(account=account)
        password_salt = bu.password_salt
        password_hash = bu.password_hash
        bep_user_id = bu.id
        if bep.models.get_hash_str(password=password, password_salt=password_salt) == password_hash:
            session_str = Session.create_session(account=account, bep_user_id=bep_user_id)
            return JsonResponse({
                "status": True,
                "session": session_str
            })
        else:
            return JsonResponse({
                "status": False,
                "error": 1
            })
    except BepUser.DoesNotExist:
        return JsonResponse({
            "status": False,
            "error": 2
        })


def register_validation(request):
    json_request = json.loads(request.body)
    account = json_request['account']
    password = json_request['password']
    phone_number = json_request['phone_number']
    username = json_request['username']
    if BepUser.create_account(account=account, password=password, phone_number=phone_number, username=username):
        return JsonResponse({
            "status": True
        })
    else:
        return JsonResponse({
            "status": False
        })


def get_session(request):
    json_request = json.loads(request.body)


def get_personal_info(request):
    json_request = json.loads(request.body)
    session_str = json_request['session']
    bep_user_id = Session.check_session(session_str)
    if bep_user_id is not None:
        try:
            bep_user = BepUser.objects.get(id=bep_user_id)
        except BepUser.DoesNotExist:
            return JsonResponse({
                "status": False,
                "error": 1
            })
        return JsonResponse({
            "status": True,
            "account": bep_user.account,
            "name": bep_user.name,
            "address": bep_user.address,
            "phone_number": bep_user.phone_number,
            "account_balance": bep_user.account_balances
        })


def deposit_50(request):
    json_request = json.loads(request.body)
    session_str = json_request['session']
    bep_user_id = Session.check_session(session_str)
    if bep_user_id is not None:
        try:
            bep_user = BepUser.objects.get(id=bep_user_id)
        except BepUser.DoesNotExist:
            return JsonResponse({
                "status": False,
                "error": 1
            })
        bep_user.account_balances += 50
        bep_user.save()
        return JsonResponse({
            "status": True
        })
    return JsonResponse({
        "status": False,
        "error": 2
    })


def create_book(request):
    try:
        book_cover = request.FILES['img']
    except django.utils.datastructures.MultiValueDictKeyError:
        return JsonResponse({
            "status": False,
            "error": 2
        })

    name = request.POST["name"]
    author = request.POST["author"]
    isbn = request.POST["isbn"]
    is_need = request.POST["is_need"] == "true"
    session = request.POST["session"]
    try:
        price = float(request.POST["price"])
    except ValueError:
        return JsonResponse({
            "status": False,
            "error": 1
        })

    bep_user_id = Session.check_session(session)
    if bep_user_id is not None:
        book = Book(publish_id=bep_user_id, name=name, price=price, is_need=is_need, isbn=isbn, author=author)
        book.cover = book_cover
        book.save()
        return JsonResponse({
            "status": True,
        })

    return JsonResponse({
        "status": False
    })


def account_balance(request):
    json_request = json.loads(request.body)
    session_str = json_request["session"]
    bep_user_id = Session.check_session(session_str)
    if bep_user_id is not None:
        try:
            user = BepUser.objects.get(id=bep_user_id)
        except BepUser.DoesNotExist:
            return JsonResponse({
                "status": False,
                "error": 1
            })
        return JsonResponse({
            "status": True,
            "account_balance": user.account_balances
        })
    return JsonResponse({
        "status": False,
        "error": 2
    })


def create_order(request):
    json_request = json.loads(request.body)
    session_str = json_request["session"]
    book_id = json_request["book_id"]
    bep_user_id = Session.check_session(session_str)
    if bep_user_id is not None:
        try:
            user = BepUser.objects.get(id=bep_user_id)
        except BepUser.DoesNotExist:
            return JsonResponse({
                "status": False,
                "error": 1
            })
        try:
            book = Book.objects.get(id=book_id)
        except Book.DoesNotExist:
            return JsonResponse({
                "status": False,
                "error": 3
            })
        book.is_sold = False
        if book.is_need:
            try:
                purchaser = BepUser.objects.get(id=book.publish_id)
            except BepUser.DoesNotExist:
                return JsonResponse({
                    "status": False,
                    "error": 4
                })
            if purchaser.account_balances < book.price:
                return JsonResponse({
                    "status": False,
                    "error": 5
                })
            else:
                order = Order(book_id=book.id, owner_id=bep_user_id, purchaser_id=book.publish_id, reserved_place="")
                purchaser.account_balances -= book.price
                purchaser.save()
                book.is_sold = True
                book.save()
                order.payed = True
                order.save()
                return JsonResponse({
                    "status": True
                })
        else:
            try:
                owner = BepUser.objects.get(id=book.publish_id)
            except BepUser.DoesNotExist:
                return JsonResponse({
                    "status": False,
                    "error": 6
                })
            if user.account_balances < book.price:
                return JsonResponse({
                    "status": False,
                    "error": 7
                })
            else:
                order = Order(book_id=book.id, owner_id=book.publish_id, purchaser_id=bep_user_id, reserved_place="")
                user.account_balances -= book.price
                user.save()
                book.is_sold = True
                book.save()
                order.payed = True
                order.save()
                return JsonResponse({
                    "status": True
                })
    else:
        return JsonResponse({
            "status": False,
            "error": 2
        })


def deprecate_order(request):
    json_request = json.loads(request.body)
    session_str = json_request['session']
    order_id = json_request['id']
    bep_user_id = Session.check_session(session_str)
    if bep_user_id is not None:
        try:
            bep_user = BepUser.objects.get(id=bep_user_id)
        except BepUser.DoesNotExist:
            return JsonResponse({
                "status": False,
                "error": 2
            })
        order = Order.objects.get(id=order_id)
        purchaser_id = order.purchaser_id
        purchaser = BepUser.objects.get(id=purchaser_id)
        book = Book.objects.get(id=order.book_id)
        purchaser.account_balances += book.price
        purchaser.save()
        order.payed = False
        order.deprecated = True
        order.save()
        return JsonResponse({
            "status": True
        })
    return JsonResponse({
        "status": False,
        "error": 1
    })


def finish_order(request):
    json_request = json.loads(request.body)
    session_str = json_request['session']
    order_id = json_request['id']
    bep_user_id = Session.check_session(session_str)
    if bep_user_id is not None:
        try:
            bep_user = BepUser.objects.get(id=bep_user_id)
        except BepUser.DoesNotExist:
            return JsonResponse({
                "status": False,
                "error": 2
            })
        order = Order.objects.get(id=order_id)
        owner_id = order.owner_id
        owner = BepUser.objects.get(id=owner_id)
        book = Book.objects.get(id=order.book_id)
        owner.account_balances += book.price
        owner.save()
        order.finished = True
        order.save()
        return JsonResponse({
            "status": True
        })
    return JsonResponse({
        "status": False,
        "error": 1
    })
