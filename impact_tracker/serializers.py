"""
Django REST Framework Serializers for impact_tracker models.
"""

from rest_framework import serializers
from django.contrib.auth.models import User
from .models import (
    SDGGoal, Activity, SDGImpact, InstitutionMetric, Department, Researcher, BenchmarkInstitution
)

# New/Updated Serializers based on Phase 2 & 3 Prompts

class DepartmentSerializer(serializers.ModelSerializer):
    """Serializer for Department model."""
    class Meta:
        model = Department
        fields = ('id', 'name', 'description')

class ResearcherSerializer(serializers.ModelSerializer):
    """Serializer for Researcher model."""
    user = serializers.StringRelatedField()
    department = serializers.StringRelatedField()

    class Meta:
        model = Researcher
        fields = ('id', 'user', 'department', 'title')

class SDGGoalSerializer(serializers.ModelSerializer):
    """Serializer for SDGGoal model."""
    projects_count = serializers.SerializerMethodField()
    publications_count = serializers.SerializerMethodField()

    class Meta:
        model = SDGGoal
        fields = ('id', 'number', 'name', 'description', 'color_code', 'icon_url',
                  'projects_count', 'publications_count')
        read_only_fields = ('id',)

    def get_projects_count(self, obj):
        return obj.activity_set.filter(activity_type='Project').count()

    def get_publications_count(self, obj):
        return obj.activity_set.filter(activity_type='Publication').count()

class ActivitySerializer(serializers.ModelSerializer):
    """
    Serializer for the Activity model, covering create, list, and detail views.
    Handles field name differences from the frontend as per Prompt 5.
    """
    # READ-ONLY fields for display
    author = ResearcherSerializer(read_only=True)
    sdgs = SDGGoalSerializer(many=True, read_only=True)
    activity_type_display = serializers.CharField(source='get_activity_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    # WRITE-ONLY fields for creation/update, matching prompt
    type = serializers.ChoiceField(
        choices=Activity.ACTIVITY_TYPES, source='activity_type', write_only=True
    )
    sdg_ids = serializers.PrimaryKeyRelatedField(
        queryset=SDGGoal.objects.all(), source='sdgs', many=True, write_only=True, allow_empty=False
    )
    author_id = serializers.PrimaryKeyRelatedField(
        queryset=Researcher.objects.all(), source='author', write_only=True
    )
    date = serializers.DateField(source='original_publication_date', write_only=True, required=False)


    class Meta:
        model = Activity
        fields = (
            # Read fields
            'id', 'title', 'description', 'impact_summary', 'activity_type', 'activity_type_display',
            'status', 'status_display', 'author', 'sdgs',
            'original_publication_date', 'external_url', 'evidence_file', 'date_created', 'updated_at',
            # Write fields
            'type', 'sdg_ids', 'author_id', 'date'
        )
        read_only_fields = ('id', 'date_created', 'updated_at', 'activity_type', 'original_publication_date')


    def create(self, validated_data):
        """
        Custom create method to handle the M2M relationship for SDGs.
        The `source` argument on the write-only fields maps them to the correct
        model fields in `validated_data`.
        """
        sdgs_data = validated_data.pop('sdgs', None)
        activity = Activity.objects.create(**validated_data)
        if sdgs_data:
            activity.sdgs.set(sdgs_data)
        return activity

class BenchmarkInstitutionSerializer(serializers.ModelSerializer):
    """Serializer for BenchmarkInstitution model."""
    class Meta:
        model = BenchmarkInstitution
        fields = ("id", "name", "total_sdg_score", "projects_count", "publications_count")


# Kept old serializers for reference or if they are still used by other parts of the application

class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model (read-only)."""
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name')
        read_only_fields = ('id',)


class SDGImpactSerializer(serializers.ModelSerializer):
    """Serializer for SDGImpact model."""
    sdg_goal_detail = SDGGoalSerializer(source='sdg_goal', read_only=True)

    class Meta:
        model = SDGImpact
        fields = ('id', 'activity', 'sdg_goal', 'sdg_goal_detail', 'score', 'justification', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')


class ActivityListSerializer(serializers.ModelSerializer):
    """Serializer for Activity model - used in list views."""
    lead_author_detail = UserSerializer(source='lead_author', read_only=True)
    activity_type_display = serializers.CharField(source='get_activity_type_display', read_only=True)

    class Meta:
        model = Activity
        fields = (
            'id', 'title', 'description', 'activity_type', 'activity_type_display',
            'lead_author', 'lead_author_detail', 'date_created', 'updated_at',
            'ai_classified', 'evidence_file'
        )
        read_only_fields = ('id', 'date_created', 'updated_at', 'ai_classified', 'evidence_file')


class ActivityDetailSerializer(serializers.ModelSerializer):
    """Serializer for Activity model - used in detail views with nested impacts."""
    lead_author_detail = UserSerializer(source='lead_author', read_only=True)
    activity_type_display = serializers.CharField(source='get_activity_type_display', read_only=True)
    sdg_impacts = SDGImpactSerializer(many=True, read_only=True)

    class Meta:
        model = Activity
        fields = (
            'id', 'title', 'description', 'activity_type', 'activity_type_display',
            'lead_author', 'lead_author_detail', 'date_created', 'updated_at',
            'ai_classified', 'evidence_file', 'sdg_impacts'
        )
        read_only_fields = ('id', 'date_created', 'updated_at', 'ai_classified')


class ActivityCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating Activity - used in POST requests."""
    class Meta:
        model = Activity
        fields = ('id', 'title', 'description', 'activity_type', 'evidence_file', 'lead_author')
        read_only_fields = ('id',)


class InstitutionMetricSerializer(serializers.ModelSerializer):
    """Serializer for InstitutionMetric model."""
    sdg_goal_detail = SDGGoalSerializer(source='sdg_goal', read_only=True)

    class Meta:
        model = InstitutionMetric
        fields = (
            'id', 'university_name', 'year', 'sdg_goal', 'sdg_goal_detail',
            'score', 'total_activities', 'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'created_at', 'updated_at')