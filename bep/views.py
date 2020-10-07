from django.shortcuts import render

from django.http import HttpResponse, JsonResponse

import bep
from bep.models import BepUser, Session, Book
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
    context = {
        "page_number": page_number,
        "books": books,
        "has_next": books.has_next(),
        "has_previous": books.has_previous(),
        "next_page_number": page_number + 1,
        "previous_page_number": page_number - 1,
    }
    return render(request, 'index.html', context)


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
    print(request.FILES)
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


