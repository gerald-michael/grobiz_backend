from allauth.account.adapter import get_adapter
from rest_auth.registration.serializers import RegisterSerializer
from rest_framework import serializers
from rest_framework.authtoken.models import Token
from phonenumber_field.serializerfields import PhoneNumberField
from phonenumber_field.phonenumber import to_python
from rest_framework.serializers import ValidationError
from accounts.models import *
from django.contrib.auth import get_user_model, authenticate
from django.utils.translation import gettext_lazy as _


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['phone_number']


class CustomLoginSerializer():
    class Meta:
        pass


class CustomPhoneNumberField(PhoneNumberField):
    def to_internal_value(self, data):
        phone_number = to_python(data)
        if phone_number and not phone_number.is_valid():
            raise ValidationError(self.error_messages["Invalid phone number"])
        return phone_number.as_e164


class ChoiceField(serializers.ChoiceField):

    def to_representation(self, obj):
        if obj == '' and self.allow_blank:
            return obj
        return self._choices[obj]

    def to_internal_value(self, data):
        # To support inserts with the value
        if data == '' and self.allow_blank:
            return ''

        for key, val in self._choices.items():
            if val == data:
                return key
        self.fail('invalid_choice', input=data)


class CustomRegisterSerializer(serializers.Serializer):
    phone_number = PhoneNumberField()
    type = ChoiceField(choices=User.Types)
    password1 = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password',
               'placeholder': 'Password'}
    )
    password2 = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password', 'placeholder': 'Confirm Password'}

    )

    def get_cleaned_data(self):
        return {
            'password1': self.validated_data.get('password1', ''),
            'password2': self.validated_data.get('password2', ''),
            'phone_number': self.validated_data.get('phone_number', ''),
            'type': self.validated_data.get('type', '')
        }

    def validate_password1(self, password):
        return get_adapter().clean_password(password)

    def validate(self, data):
        if data['password1'] != data['password2']:
            raise serializers.ValidationError(
                _("The two password fields didn't match."))
        return data

    def save(self, request):
        self.cleaned_data = self.get_cleaned_data()
        phone_number = self.cleaned_data.get('phone_number')
        password = self.cleaned_data.get('password1')
        user = User.objects.create_user(
            phone_number=phone_number, type=self.cleaned_data.get('type'), password=password, is_staff=False)
        print(user)
        return user


class CustomLoginSerializer(serializers.Serializer):
    phone_number = PhoneNumberField()
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password',
               'placeholder': 'Password'}
    )

    def get_cleaned_data(self):
        return {
            'phone_number': self.validated_data.get('phone_number', ''),
            'password': self.validated_data.get('password', ''),
        }

    def validate_password(self, password):
        return get_adapter().clean_password(password)

    def authenticate(self, **kwargs):
        return authenticate(self.context['request'], **kwargs)

    def validate(self, data):
        if not data['phone_number']:
            raise serializers.ValidationError(
                _("Phone number is required"))

        if not data['password']:
            raise serializers.ValidationError(
                _("Password is required"))

        user = self.authenticate(
            phone_number=data['phone_number'], password=data['password'])
        data['user'] = user
        return data


class TokenSerializer(serializers.ModelSerializer):
    phone_number = serializers.SerializerMethodField()

    class Meta:
        model = Token
        fields = ('key', 'phone_number')

    def get_phone_number(self, obj):
        serializer_data = UserSerializer(
            obj.user
        ).data
        return (
            serializer_data.get('phone_number')
        )


class SmeProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = SmeProfile
        exclude = ('user', 'status',)
