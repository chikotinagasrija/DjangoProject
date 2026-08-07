from django.contrib.auth import authenticate
from rest_framework import serializers
from .models import CustomUser, UserProfile


class RegistrationSerializer(serializers.ModelSerializer):

    class Meta:
        model = CustomUser
        fields = [
            "first_name",
            "last_name",
            "email",
            "password",
        ]

        extra_kwargs = {
            "password": {
                "write_only": True
            }
        }

    def validate_email(self, value):
        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                "A user with this email already exists."
            )

        return value

    def validate_password(self, value):

        if len(value) < 8:
            raise serializers.ValidationError(
                "Password must be at least 8 characters long."
            )

        if not any(char.isupper() for char in value):
            raise serializers.ValidationError(
                "Password must contain at least one uppercase letter."
            )

        if not any(char.islower() for char in value):
            raise serializers.ValidationError(
                "Password must contain at least one lowercase letter."
            )

        if not any(char.isdigit() for char in value):
            raise serializers.ValidationError(
                "Password must contain at least one number."
            )

        return value

    def create(self, validated_data):

        user = CustomUser.objects.create_user(
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
            email=validated_data["email"],
            password=validated_data["password"]
        )

        return user


class LoginSerializer(serializers.Serializer):

    email = serializers.EmailField()

    password = serializers.CharField(
        write_only=True
    )

    def validate(self, data):

        email = data.get("email")
        password = data.get("password")

        user = authenticate(
            email=email,
            password=password
        )

        if user is None:
            raise serializers.ValidationError(
                "Invalid email or password."
            )

        data["user"] = user

        return data


class UserProfileSerializer(serializers.ModelSerializer):

    class Meta:

        model = UserProfile

        fields = [
            "id",
            "phone_number",
            "date_of_birth",
            "gender",
            "profile_picture",
            "address",
            "city",
            "state",
            "country",
            "pincode",
            "bio",
            "created_at",
            "updated_at",
            "created_by",
            "updated_by"
        ]
        
    def validate_phone_number(self, value):
        if not value.isdigit():
            raise serializers.ValidationError(
                "Phone number must contain only digits."
            )

        if len(value) != 10:
            raise serializers.ValidationError(
                "Phone number must be exactly 10 digits."
            )

        return value

    def validate(self, data):
        required_fields = ["phone_number", "city", "country"]

        for field in required_fields:
            if not data.get(field):
                raise serializers.ValidationError(
                    {field: f"{field} is required."}
                )

        return data    


class ProfileImageSerializer(serializers.ModelSerializer):

    class Meta:

        model = UserProfile

        fields = [
            "profile_picture"
        ]

    def validate_profile_picture(self, value):

        allowed_types = [
            "image/jpeg",
            "image/png",
            "image/jpg"
        ]

        if value.content_type not in allowed_types:
            raise serializers.ValidationError(
                "Only JPG, JPEG and PNG images are allowed."
            )

        if value.size > 2 * 1024 * 1024:
            raise serializers.ValidationError(
                "Image size should not exceed 2MB."
            )

        return value
