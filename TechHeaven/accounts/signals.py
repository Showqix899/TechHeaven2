from django.db.models.signals import post_delete,post_save
from django.contrib.auth.signals import user_logged_in,user_logged_out,user_login_failed
from activity_log.models import ActivityLog
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.utils.timezone import now
import logging


logger = logging.getLogger(__name__)

#user model
User=get_user_model()

#user log in log
@receiver(user_logged_in)
def user_login_activity(sender,request,user,**kwargs):

    logger.info(f'{user.email} logged in')

    log=ActivityLog.objects.create(
        event=f"{user.email} logged in",
        action="login",
        payload={
            "time": str(now())
        }
        
    )


#user user logout log
@receiver(user_logged_out)
def user_logout_activity(sender, request, user, **kwargs):
    logger.info(f'{user.email} logged out')

    ActivityLog.objects.create(
        event=f"{user.email} logged out",
        action="logout",
        payload={
            "user_id": str(user.id),
            "email": user.email,
            "timestamp": str(now())
        }
    )



#user login fail log
@receiver(user_login_failed)
def user_login_fail_activity(sender,request,**kwargs):

    logger.warning(f'login failed')

    log=ActivityLog.objects.create(
        event=f" tried to login",
        action="login failed",
        payload={
            "user_id":" ",
            "email":" ",
            "timestamp": str(now())
        }
        
    )

#user sign up log
@receiver(post_save,sender=User)
def user_sign_up_activity(sender,instance,**kwargs):

    log=ActivityLog.objects.create(
        event=f"{instance.email} tried to login",
        action="login failed",

        payload={
                "user_id": str(instance.id),
                "email": instance.email,
                "timestamp": str(now())
            }
        
    )


#user delete signal log
@receiver(post_delete, sender=User)
def user_delete_activity(sender, instance, **kwargs):
    ActivityLog.objects.create(
        event=f"{instance.email} deleted account",
        action="user delete",
        payload={
            "user_id": str(instance.id),
            "email": instance.email,
            "timestamp": str(now())
        }
    )
