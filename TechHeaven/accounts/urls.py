# urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('admin-invite/', views.admin_invitation_generator, name='admin_invite'),
    path('user/admin-registration/<token>/', views.admin_registration_view, name='admin_registration'),
    path('signup/', views.signup_view, name='signup'),
    path('activate/<uidb64>/<token>/', views.activate_account, name='activate'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('password-reset/', views.password_reset_request, name='password_reset_request'),
    path('reset/<uidb64>/<token>/', views.password_reset_confirm, name='password_reset_confirm'),
    path('user/list/',views.user_list,name='user_list'),
    path('user/search/',views.user_search,name='user_search'),
    path('user/delete/<int:user_id>',views.user_delete,name='user_delete'),
    path('user/update/<int:user_id>/',views.update_user,name='update_user'),
    path('user/my-account/<int:user_id>/',views.my_account,name="my_account"),
]
