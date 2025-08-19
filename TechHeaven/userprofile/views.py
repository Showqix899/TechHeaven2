from django.shortcuts import render
from django.shortcuts import render, redirect, get_object_or_404
from .models import CustomUserProfile, UserAddress
from .forms import CustomUserProfileForm, UserAddressForm
from django.contrib.auth.decorators import login_required

# Create your views here.



# Profile detail view
@login_required
def profile_detail(request):

    user= request.user
    profile = get_object_or_404(CustomUserProfile, user=user)
    addresses = UserAddress.objects.filter(profile=profile)
    
    return render(request, 'userprofile/profile_detail.html', {
        'profile': profile,
        'addresses': addresses
    })






#profile update
@login_required
def profile_update(request):
    profile = get_object_or_404(CustomUserProfile, user=request.user)
    if request.method == 'POST':
        form = CustomUserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('profile_detail')
    else:
        form = CustomUserProfileForm(instance=profile)
    return render(request, 'userprofile/profile_form.html', {'form': form})



#address update

@login_required
def address_create(request):
    if request.method == 'POST':
        form = UserAddressForm(request.POST, user=request.user)
        if form.is_valid():
            address = form.save(commit=False)
            address.profile = request.user.profile
            address.save()
            return redirect('profile_detail')
        
    else:
        form = UserAddressForm(user=request.user)
    return render(request, 'userprofile/address_form.html', {'form': form})




# Update Address
@login_required
def address_update(request, pk):
    profile = get_object_or_404(CustomUserProfile, user=request.user)
    address = get_object_or_404(UserAddress, pk=pk, profile=profile)
    if request.method == 'POST':
        form = UserAddressForm(request.POST, instance=address)
        if form.is_valid():
            form.save()
            return redirect('profile_detail')  # Change to your profile page name
    else:
        form = UserAddressForm(instance=address)
    return render(request, 'userprofile/address_update.html', {'form': form})

# Delete Address
@login_required
def address_delete(request, pk):
    profile = get_object_or_404(CustomUserProfile, user=request.user)
    address = get_object_or_404(UserAddress, pk=pk, profile=profile)
    if request.method == 'POST':
        address.delete()
        return redirect('profile_detail')  # Change to your profile page name
    return render(request, 'userprofile/address_delete.html', {'address': address})