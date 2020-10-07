from django.db import models
import random
import hashlib


# Create your models here.


class Book(models.Model):
    id = models.AutoField(primary_key=True)
    publish_id = models.IntegerField(editable=False)
    name = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=7, decimal_places=2)
    is_need = models.BooleanField(default=False)
    isbn = models.CharField(max_length=20, default="")
    author = models.CharField(max_length=50, default="")
    pub_time = models.DateTimeField(auto_now=True, editable=False)
    cover = models.ImageField(upload_to='uploads/%Y/%m/%d/')


class Order(models.Model):
    id = models.AutoField(primary_key=True)
    book_id = models.IntegerField(editable=False)
    owner_id = models.IntegerField(editable=False, unique=True)
    purchaser_id = models.IntegerField(editable=False, unique=False)
    reserved_place = models.CharField(max_length=100)
    pub_time = models.DateTimeField(auto_now=True, editable=False)

    payed = models.BooleanField(default=False)
    deprecated = models.BooleanField(default=False)
    finished = models.BooleanField(default=False)

    rate = models.IntegerField(default=5)


class Session(models.Model):
    id = models.AutoField(primary_key=True)
    bep_user_id = models.IntegerField(editable=False)
    session_str = models.CharField(max_length=200)

    @staticmethod
    def create_session(account, bep_user_id):
        session_str = account + get_salt_str()
        Session(bep_user_id=bep_user_id, session_str=session_str).save()
        return session_str

    @staticmethod
    def check_session(session_str):
        try:
            session = Session.objects.get(session_str=session_str)
        except Session.DoesNotExist:
            return None
        return session.bep_user_id


class BepUser(models.Model):
    id = models.AutoField(primary_key=True)

    account = models.CharField(max_length=30, editable=False)
    password_hash = models.CharField(max_length=100, editable=False)
    password_salt = models.CharField(max_length=100, editable=False)
    name = models.CharField(max_length=50)
    account_balances = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    phone_number = models.CharField(max_length=20)
    deals = models.IntegerField(default=0)
    address = models.CharField(max_length=100, default="")

    @staticmethod
    def create_account(account, password, username, phone_number) -> bool:
        try:
            BepUser.objects.get(account=account)
        except BepUser.DoesNotExist:
            mid = BepUser(account=account, name=username)
            password_salt = get_salt_str()
            password_hash = get_hash_str(password=password, password_salt=password_salt)
            mid.password_salt = password_salt
            mid.password_hash = password_hash
            mid.phone_number = phone_number
            mid.save()
            return True

        return False


def get_salt_str():
    # 获取加密盐字符串
    return random.random().__str__()[2:]


def get_hash_str(password, password_salt):
    # 获取密码哈希值
    mid = hashlib.sha3_256()
    mid.update(bytes(password, encoding="utf8"))
    mid.update(bytes(password_salt, encoding="utf8"))
    return mid.hexdigest()
