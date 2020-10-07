from django.urls import path, include
import bep.views
urlpatterns = [
    path("validation/login/", bep.views.login_validation),
    path("validation/register/", bep.views.register_validation),
    path("personal_info/", bep.views.get_personal_info),
    path("deposit_50/", bep.views.deposit_50),
    path("create_book/", bep.views.create_book)
]