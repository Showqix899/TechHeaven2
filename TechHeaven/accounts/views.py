from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate, get_user_model
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.http import HttpResponse
from django.urls import reverse
from django.conf import settings
from .forms import SignUpForm, CustomAuthenticationForm, CustomSetPasswordForm, CustomPasswordResetForm
from .token import account_activation_token
from .models import AdminInvitation
from .forms import AdminInvitationForm
from .task import email_send
from products.models import Product
from order.models import Order,OrderItem
from payment.models import PaymentHistory
from .models import CustomUser
from .forms import CustomUserUpdateForm
from django.contrib.auth.decorators import login_required
from order.models import Order,OrderItem
from payment.models import PaymentHistory
from activity_log.models import ActivityLog


User = get_user_model()#get user model

#sign up view
def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  # make sure still inactive (redundant safety)
            user.save()

            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = account_activation_token.make_token(user)
            activation_link = request.build_absolute_uri(reverse('activate', args=[uid, token]))

            message = f'Hi {user.email}, click here to activate your account: {activation_link}'
            email_send.delay('Activate your account', message, settings.EMAIL_HOST_USER, [user.email])
            print(f"Activation link: {activation_link}")  # Debugging line

            return render(request, 'accounts/email_sent.html', {'email': user.email})
        else:
            return HttpResponse('Invalid form submission.')
    else:
        form = SignUpForm()
    return render(request, 'accounts/signup.html', {'form': form})


#account activation view
def activate_account(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        return HttpResponse('Account activated successfully! <a href="/login/">Login here</a>')
    else:
        return HttpResponse('Activation link invalid!')



#login view
def login_view(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('/')
    else:
        form = CustomAuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form})





#logout view
def logout_view(request):
    logout(request)
    return redirect('login')




# Password reset views
def password_reset_request(request):
    if request.method == 'POST':
        form = CustomPasswordResetForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            user = User.objects.filter(email=email).first()
            if user:
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                token = default_token_generator.make_token(user)
                reset_link = request.build_absolute_uri(reverse('password_reset_confirm', args=[uid, token]))
                message = f'Hi {user.email}, click here to reset your password: {reset_link}'
                email_send.delay('Password Reset', message, settings.EMAIL_HOST_USER, [user.email])

            return render(request, 'accounts/email_sent.html', {'email': email})
    else:
        form = CustomPasswordResetForm()
    return render(request, 'accounts/password_reset_request.html', {'form': form})



# Password reset confirmation view
def password_reset_confirm(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            form = CustomSetPasswordForm(user, request.POST)
            if form.is_valid():
                form.save()
                return HttpResponse('Password reset successful! <a href="/login/">Login here</a>')
        else:
            form = CustomSetPasswordForm(user)
        return render(request, 'accounts/reset_password_form.html', {'form': form})
    else:
        return HttpResponse('Reset link invalid or expired.')


from django.utils import timezone
from django.contrib.sites.shortcuts import get_current_site

#Admin invitation view 
def admin_invitation_generator(request):

    if not request.user.role == "ADMIN":
        return HttpResponse("need to be an Admin. You are not allowed")
    
    form = AdminInvitationForm(request.POST)

    if request.method == 'POST':

        if form.is_valid():
            email = form.cleaned_data['email']
            user = User.objects.filter(email=email).first()

            expires_at = timezone.now() + timezone.timedelta(days=7)
            invitation = AdminInvitation.objects.create(
                created_by=request.user,
                expires_at=expires_at,
                admin=email
            )

            if user and user.role=='USER':
                link = f'http://{get_current_site(request).domain}/user/admin-registration/{invitation.token}/'
                message = f'Hi, click here to register as an admin: {link}'
                email_send.delay(
                'Admin Invitation',
                message,
                settings.EMAIL_HOST_USER,
                [email]
                )
                

            expires_at = timezone.now() + timezone.timedelta(days=7)
            invitation = AdminInvitation.objects.create(
                created_by=request.user,
                expires_at=expires_at,
                admin=email
            )

            link = f'http://{get_current_site(request).domain}/user/admin-registration/{invitation.token}/'
            message = f'Hi, click here to register as an admin: {link}'
            email_send.delay(
                'Admin Invitation',
                message,
                settings.EMAIL_HOST_USER,
                [email]
            )
            return render(request, 'accounts/message.html', {'email': email,'message': 'admin Invitation sent successfully!'})
        
    return  render(request, 'accounts/admin_invaitation.html', {'form': form})


#admin registration view
from django.shortcuts import get_object_or_404
def admin_registration_view(request, token):
    invitation = get_object_or_404(AdminInvitation, token=token, is_used=False)

    if request.method == 'POST':
        form = SignUpForm(request.POST)
        email = form.data.get('email')
        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)
            user.role= 'ADMIN'
            user.save()

        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = True  # Admins are active by default
            user.role = 'ADMIN'  # Set role to ADMIN
            user.save()

            invitation.is_used = True
            invitation.save()

            login(request, user)
            return HttpResponse('Admin registration successful! <a href="/login/">Login here</a>')
    else:
        form = SignUpForm()

    return render(request, 'accounts/admin_Reg.html', {'form': form})


#user list
def user_list(request):

    try:
        users=User.objects.all()

        return render (request,'accounts/user_list.html',{'users':users})
    except User.DoesNotExist:

        return render(request, 'accounts/error_message.html', {
            'message': 'No user found'
        })



#search user
def user_search(request):

    if not request.user.role == "ADMIN":
        return HttpResponse("need to be an Admin. You are not allowed")

    query=request.GET.get('q','').strip()
    user=None
    order_item_list=[]
    if query:

        try:

            user=User.objects.get(email=query)
            orders=Order.objects.filter(user=user.id)
            payment_list=PaymentHistory.objects.filter(user=user.id)

            for order in orders:

                order_items=OrderItem.objects.filter(order=order)
                order_item_list.extend(order_items)

        except User.DoesNotExist:

            return render(request, 'accounts/error_message.html', {
            'message': f'No user found matching "{query}".'
        })

    else:
        return render(request, 'accounts/error_message.html', {
            'message': 'Please enter a search query.'
        })
    
    
    return render(request, 'accounts/user_details.html', {
        'user': user,
        'query': query,
        'orders':order_item_list,
        'payment_list':payment_list    
        })

#user details
def user_delete(request,user_id):

    if not request.user.role == "ADMIN":

        return HttpResponse("Not Allowed")

    try:

        user=User.objects.get(id=user_id)
        user.delete()

        return redirect('user_list')
            

    except User.DoesNotExist:

            return render(request, 'accounts/error_message.html', {
            'message': f'No user found matching'
        })


@login_required
def update_user(request, user_id):
    if not request.user.role == "ADMIN":
        return HttpResponse("need to be an Admin. You are not allowed")
     
    user = get_object_or_404(CustomUser, id=user_id)

    if request.method == 'POST':
        form = CustomUserUpdateForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('user_list')  # or any other page
    else:
        form = CustomUserUpdateForm(instance=user)

    return render(request, 'accounts/user_update.html', {'form': form})

@login_required
def my_account(request, user_id):
    user = get_object_or_404(User, id=user_id)
    total_spent=0

    # Fetch all orders for the user
    orders = Order.objects.filter(user=user)

    for order in orders:

        total_spent+=order.total_amount

    # Gather all items from each order
    order_items = OrderItem.objects.filter(order__in=orders)

    # Fetch payment history for the user
    payment_list = PaymentHistory.objects.filter(user=user)

    # Fetch recent activity logs (limit to recent 20 for example)
    activity_logs = ActivityLog.objects.filter(payload__user_id=str(user.id)).order_by('-created_at')[:20]

    return render(request, 'accounts/my_account.html', {
        'user': user,
        'orders': orders,
        'order_items': order_items,
        'payment_list': payment_list,
        'activity_logs': activity_logs,
        'total_spent':total_spent
    })