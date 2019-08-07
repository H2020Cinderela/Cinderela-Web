from rest_framework import serializers
from rest_framework_nested.serializers import NestedHyperlinkedModelSerializer

from repair.apps.asmfa.models import Activity
from repair.apps.changes.models import (SolutionCategory,
                                        Solution,
                                        ImplementationQuestion,
                                        SolutionPart,
                                        AffectedFlow,
                                        PossibleImplementationArea,
                                        Scheme,
                                        FlowReference
                                        )

from repair.apps.login.serializers import (InCasestudyField,
                                           UserInCasestudyField,
                                           InCaseStudyIdentityField,
                                           IdentityFieldMixin,
                                           CreateWithUserInCasestudyMixin,
                                           IDRelatedField)
from repair.apps.statusquo.models import SpatialChoice
from repair.apps.utils.serializers import EnumField


class SolutionCategorySerializer(CreateWithUserInCasestudyMixin,
                                 NestedHyperlinkedModelSerializer):
    parent_lookup_kwargs = {
        'casestudy_pk': 'keyflow__casestudy__id',
        'keyflow_pk': 'keyflow__id',
    }

    class Meta:
        model = SolutionCategory
        fields = ('url', 'id', 'name')
        read_only_fields = ('url', 'id')


class SolutionDetailCreateMixin:
    def create(self, validated_data):
        """Create a new solution quantity"""
        url_pks = self.context['request'].session['url_pks']
        solution_pk = url_pks['solution_pk']
        solution = Solution.objects.get(id=solution_pk)

        obj = self.Meta.model.objects.create(
            solution=solution,
            **validated_data)
        return obj


class ImplementationQuestionSerializer(SolutionDetailCreateMixin,
                                       NestedHyperlinkedModelSerializer):
    solution = IDRelatedField(read_only=True)
    parent_lookup_kwargs = {
        'casestudy_pk': 'solution__solution_category__keyflow__casestudy__id',
        'keyflow_pk': 'solution__solution_category__keyflow__id',
        'solution_pk': 'solution__id'
    }

    class Meta:
        model = ImplementationQuestion
        fields = ('url', 'id', 'solution', 'question', 'select_values',
                  'step', 'min_value', 'max_value', 'is_absolute')
        extra_kwargs = {'step': {'required': False},
                        'select_values': {'required': False}}


class PossibleImplementationAreaSerializer(SolutionDetailCreateMixin,
                                           NestedHyperlinkedModelSerializer):
    solution = IDRelatedField(read_only=True)
    edit_mask = serializers.ReadOnlyField()
    parent_lookup_kwargs = {
        'casestudy_pk': 'solution__solution_category__keyflow__casestudy__id',
        'keyflow_pk': 'solution__solution_category__keyflow__id',
        'solution_pk': 'solution__id'
    }

    class Meta:
        model = PossibleImplementationArea
        fields = ('url', 'id', 'solution', 'question', 'geom', 'edit_mask')


class SolutionSerializer(CreateWithUserInCasestudyMixin,
                         NestedHyperlinkedModelSerializer):
    parent_lookup_kwargs = {
        'casestudy_pk': 'solution_category__keyflow__casestudy__id',
        'keyflow_pk': 'solution_category__keyflow__id'
    }

    solution_category = IDRelatedField()
    currentstate_image = serializers.ImageField(required=False, allow_null=True)
    activities_image = serializers.ImageField(required=False, allow_null=True)
    effect_image = serializers.ImageField(required=False, allow_null=True)
    implementation_count = serializers.SerializerMethodField()
    affected_activities = serializers.SerializerMethodField()

    class Meta:
        model = Solution
        fields = ('url', 'id', 'name', 'description',
                  'documentation', 'solution_category',
                  'activities_image',
                  'currentstate_image', 'effect_image',
                  'implementation_count',
                  'affected_activities'
                  )
        read_only_fields = ('url', 'id', )
        extra_kwargs = {
            'description': {'required': False},
            'documentation': {'required': False},
        }

    def get_implementation_count(self, obj):
        return obj.strategy_set.count()

    def get_affected_activities(self, obj):
        parts = SolutionPart.objects.filter(solution=obj)
        activities = parts.values_list(
            'flow_reference__origin_activity__id',
            'flow_reference__destination_activity__id',
            'flow_changes__origin_activity__id',
            'flow_changes__destination_activity__id',
            'affected_flows__destination_activity__id',
            'affected_flows__origin_activity__id'
        )
        activities = set([i for s in activities for i in s])
        try:
            activities.remove(None)
        except:
            pass
        return activities


class AffectedFlowSerializer(CreateWithUserInCasestudyMixin,
                             serializers.ModelSerializer):

    class Meta:
        model = AffectedFlow
        fields = ('id', 'origin_activity', 'destination_activity',
                  'material', 'process')
        extra_kwargs = {
            'process': {'required': False},
        }


class FlowReferenceSerializer(CreateWithUserInCasestudyMixin,
                             NestedHyperlinkedModelSerializer):

    origin_activity = IDRelatedField(
        required=False, allow_null=True)
    destination_activity = IDRelatedField(
        required=False, allow_null=True)
    material = IDRelatedField(
        required=False, allow_null=True)
    process = IDRelatedField(
        required=False, allow_null=True)
    origin_area = IDRelatedField(
        required=False, allow_null=True)
    destination_area = IDRelatedField(
        required=False, allow_null=True)


class SolutionPartSerializer(CreateWithUserInCasestudyMixin,
                             NestedHyperlinkedModelSerializer):
    solution = IDRelatedField(read_only=True)
    parent_lookup_kwargs = {
        'casestudy_pk': 'solution__solution_category__keyflow__casestudy__id',
        'keyflow_pk': 'solution__solution_category__keyflow__id',
        'solution_pk': 'solution__id'
    }
    scheme = EnumField(enum=Scheme)
    flow_reference = FlowReferenceSerializer(allow_null=True)
    flow_changes = FlowReferenceSerializer(allow_null=True, required=False)

    affected_flows = AffectedFlowSerializer(source='affected_flows', many=True)
    question = IDRelatedField(allow_null=True)

    # ToDo: serialize affected flows as part of this serializer

    class Meta:
        model = SolutionPart
        fields = ('url', 'id', 'name', 'solution',
                  'scheme', 'documentation',
                  'flow_references',
                  'flow_changes',
                  'question', 'a', 'b',
                  'priority',
                  'affected_flows',
                  'is_absolute',
                  )
        read_only_fields = ('url', 'id', 'solution')
        extra_kwargs = {
            'documentation': {'required': False, 'allow_blank': True},
            'is_absolute': {'required': False}
        }

    def update(self, instance, validated_data):
        affected_flows = validated_data.pop('affected_flows', None)
        instance = super().update(instance, validated_data)
        if affected_flows:
            AffectedFlow.objects.filter(solution_part=instance).delete()
            for f in affected_flows:
                flow = AffectedFlow(solution_part=instance, **f)
                flow.save()
        instance.save()
        return instance

