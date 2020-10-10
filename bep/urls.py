from django.urls import path, include
import bep.views
urlpatterns = [
    path("validation/login/", bep.views.login_validation),
    path("validation/register/", bep.views.register_validation),
    path("personal_info/", bep.views.get_personal_info),
    path("deposit_50/", bep.views.deposit_50),
    path("create_book/", bep.views.create_book),
    path("account_balance/", bep.views.account_balance),
    path("create_order/", bep.views.create_order),
    path("deprecate_order/", bep.views.deprecate_order),
    path("finish_order/", bep.views.finish_order),
]
