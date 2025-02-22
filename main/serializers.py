from rest_framework import serializers

class SignupSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

class SigninSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

class UserProfileSerializer(serializers.Serializer):
    uid = serializers.CharField()
    email = serializers.EmailField()
    display_name = serializers.CharField(required=False, allow_null=True)
    photo_url = serializers.URLField(required=False, allow_null=True)
    email_verified = serializers.BooleanField()
    created_at = serializers.DateTimeField()
    last_sign_in = serializers.DateTimeField()
