from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from phonenumber_field.modelfields import PhoneNumberField
from django.db.models.signals import post_save, pre_save
from django.contrib.auth import get_user_model
from django.dispatch import Signal
from django.core.mail import send_mail
from django.utils import timezone

# Create your models here.


def upload_profile_image(instance, filename):
    return "profile/{user}/{filename}".format(user=instance.user, filename=filename)


def upload_business_info(instance, filename):
    return "profile/{user}/business_info/{filename}".format(user=instance.user, filename=filename)


user_deleted = Signal(providing_args=['user'])


class DeleteError(Exception):
    pass


class UserManager(BaseUserManager):
    def __create_user(
        self,
        phone_number,
        type,
        password,
        is_staff,
        is_superuser,
        is_verified,
    ):
        if not phone_number:
            raise ValueError('Users must have an phone number')
        if not password:
            raise ValueError('Users must have an password')
        if not type:
            raise ValueError('Users must have belong to a type')
        user = self.model(
            phone_number=phone_number,
            type=type,
            is_staff=is_staff,
            is_superuser=is_superuser,
            is_verified=is_verified
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, phone_number, type, password, is_staff):
        """
        Creates and saves a User with the given phone_number, and password.
        """
        return self.__create_user(phone_number, type, password, is_staff, False, False)

    def create_superuser(self, phone_number, type, password):
        return self.__create_user(phone_number, type, password, True, True, True)

    def delete_user(self, user_obj):
        user_obj.is_active = False
        user_obj.save()

        user_deleted.send(sender=self.__class__, user=user_obj)


class User(AbstractBaseUser, PermissionsMixin):
    class Types(models.TextChoices):
        SME = "SME", "Sme"
        INVESTOR = "INVESTOR", "Investor"

    type = models.CharField(_("Type"), max_length=50,
                            choices=Types.choices, default=Types.SME)
    phone_number = PhoneNumberField(
        _('Phone Number'),
        unique=True,
        db_index=True,
    )
    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_(
            'Designates whether the user can log into this admin site.'),
    )
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)

    is_verified = models.BooleanField(_('verified'), default=False)

    EMAIL_FIELD = None
    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = ['type']

    objects = UserManager()

    def __str__(self):
        return str(self.phone_number)

    def has_verified_phone_number(self):
        return self.is_verified

    def delete(self, force_drop=False, *args, **kwargs):
        if force_drop:
            super().delete(*args, **kwargs)
        else:
            raise DeleteError(
                'UserProfile.objects.delete_user() should be used.',
            )

    def get_short_name(self):
        return self.phone_number

    def get_full_name(self):
        """Return string representation."""
        return str(self)

    def save(self, *args, **kwargs):
        return super().save(*args, **kwargs)


class SmeManager():
    def get_queryset(self, *args, **kwargs):
        return super().get_queryset(*args, **kwargs).filter(type=User.Types.SME)


class Sme(User):
    base_type = User.Types.SME
    objects = SmeManager()

    @property
    def profile(self):
        return self.smeprofile

    class Meta:
        proxy = True


class InvestorManager(models.Manager):
    def get_queryset(self, *args, **kwargs):
        return super().get_queryset(*args, **kwargs).filter(type=User.Types.INVESTOR)


class Investor(User):
    base_type = User.Types.INVESTOR
    objects = InvestorManager()

    @property
    def profile(self):
        return self.investorprofile

    class Meta:
        proxy = True


class SmeProfile(models.Model):
    class Status(models.TextChoices):
        DENIED = 'DENIED', "denied"
        PENDING = "PENDING", "pending"
        APPROVED = "APPROVED", "approved"
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_image = models.ImageField(upload_to=upload_profile_image)
    description = models.TextField()
    name = models.CharField(_(
        "Name of Business"),
        blank=True,
        max_length=255,
        # unique=True,
    )
    status = models.CharField(
        _("Status"), max_length=50, choices=Status.choices, default=Status.PENDING)
    tin = models.CharField(max_length=120)
    latitude = models.DecimalField(
        max_digits=22, decimal_places=16, blank=True, null=True)
    longitude = models.DecimalField(
        max_digits=22, decimal_places=16, blank=True, null=True)


class InvestorProfile(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="investor_profile")
    profile_image = models.ImageField(upload_to=upload_profile_image)
    name = models.CharField(_(
        "Name of Investor"),
        blank=True,
        max_length=255,
        # unique=True,
    )


class BusinessImage(models.Model):
    sme_profile = models.ForeignKey(
        SmeProfile, on_delete=models.CASCADE, related_name="sme_images")
    image = models.ImageField(upload_to=upload_business_info)


def create_profile(sender, instance, created, *args, **kwargs):
    if created:
        if instance.type == User.Types.SME:
            SmeProfile.objects.create(user=instance)
        elif instance.type == User.Types.INVESTOR:
            InvestorProfile.objects.create(user=instance)


post_save.connect(create_profile, sender=User)
