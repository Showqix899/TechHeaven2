from celery import shared_task
from .models import CustomUserProfile
from django.contrib.auth import get_user_model

User = get_user_model()

@shared_task
def user_profile_creation(user_id):
    """
    Task to create a user profile when a new user is created.
    """
    try:
        user = User.objects.get(id=user_id)
        profile= CustomUserProfile.objects.create(user=user)
        profile.save()
        print(f"Profile created for user: {user.email}")
    except User.DoesNotExist:
        print(f"User with ID {user_id} does not exist.")
    except Exception as e:
        print(f"An error occurred while creating profile for user ID {user_id}: {e}")
        

