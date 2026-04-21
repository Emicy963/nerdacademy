from rest_framework import serializers
from .models import Institution


class InstitutionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Institution
        fields = [
            "id",
            "name",
            "slug",
            "institution_prefix",
            "province",
            "email",
            "phone",
            "address",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "slug", "created_at", "updated_at"]


class InstitutionUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Institution
        fields = ["name", "institution_prefix", "province", "email", "phone", "address", "is_active"]

    def validate_institution_prefix(self, value):
        return value.strip().upper() if value else ""
