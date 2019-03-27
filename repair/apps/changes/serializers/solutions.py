from rest_framework import serializers
from rest_framework_nested.serializers import NestedHyperlinkedModelSerializer

from repair.apps.asmfa.models import Activity
from repair.apps.changes.models import (SolutionCategory,
                                        Solution,
                                        ImplementationQuestion,
                                        SolutionPart
                                        )

from repair.apps.login.serializers import (InCasestudyField,
                                           UserInCasestudyField,
                                           InCaseStudyIdentityField,
                                           IdentityFieldMixin,
                                           CreateWithUserInCasestudyMixin,
                                           IDRelatedField)


class SolutionCategoryField(InCasestudyField):
    parent_lookup_kwargs = {
        'casestudy_pk': 'solution_category__keyflow__casestudy__id',
        'keyflow_pk': 'solution_category__keyflow__id'
    }


class SolutionField(InCasestudyField):
    parent_lookup_kwargs = {
        'casestudy_pk': 'solution_category__keyflow__casestudy__id',
        'keyflow_pk': 'solution_category__keyflow__id',
        'solutioncategory_pk': 'solution_category__id'
    }


class SolutionSetField(InCasestudyField):
    """Returns a List of links to the solutions"""
    lookup_url_kwarg = 'solutioncategory_pk'
    parent_lookup_kwargs = {
        'casestudy_pk': 'solution_category__keyflow__casestudy__id',
        'keyflow_pk': 'solution_category__keyflow__id',
        'solutioncategory_pk': 'solution_category__id'
    }


class SolutionListField(IdentityFieldMixin, SolutionSetField):
    """Returns a Link to the solutions--list view"""
    lookup_url_kwarg = 'solutioncategory_pk'
    parent_lookup_kwargs = {
        'casestudy_pk': 'keyflow__casestudy__id',
        'keyflow_pk': 'keyflow__id',
        'solutioncategory_pk': 'id'
    }


class SolutionSetSerializer(NestedHyperlinkedModelSerializer):
    parent_lookup_kwargs = {
        'casestudy_pk': 'solution_category__keyflow__casestudy__id',
        'keyflow_pk': 'solution_category__keyflow__id',
        'solutioncategory_pk': 'solution_category__id'
    }

    class Meta:
        model = Solution
        fields = ('url', 'id', 'name')


class SolutionCategorySerializer(CreateWithUserInCasestudyMixin,
                                 NestedHyperlinkedModelSerializer):
    parent_lookup_kwargs = {
        'casestudy_pk': 'keyflow__casestudy__id',
        'keyflow_pk': 'keyflow__id',
    }
    solution_set = SolutionListField(
        view_name='solution-list')
    solution_list = SolutionSetField(
        source='solution_set',
        view_name='solution-detail',
        many=True,
        read_only=True,
    )
    user = UserInCasestudyField(
        view_name='userincasestudy-detail', read_only=True
    )
    keyflow = IDRelatedField(required=False)

    class Meta:
        model = SolutionCategory
        fields = ('url', 'id', 'name', 'user', 'keyflow', 'solution_set', 'solution_list')
        read_only_fields = ('url', 'id')


class SolutionCategoryPostSerializer(SolutionCategorySerializer):
    class Meta:
        model = SolutionCategory
        fields = ('url', 'id', 'name', 'user', 'solution_set', 'solution_list')
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
    unit = IDRelatedField()
    solution = IDRelatedField(read_only=True)
    parent_lookup_kwargs = {
        'casestudy_pk': 'solution__solution_category__keyflow__casestudy__id',
        'keyflow_pk': 'solution__solution_category__keyflow__id',
        'solutioncategory_pk': 'solution__solution_category__id',
        'solution_pk': 'solution__id'
    }

    class Meta:
        model = ImplementationQuestion
        fields = ('url', 'id', 'question', 'unit', 'select_values', 'steps',
                  'min_value', 'max_value', 'is_absolute')
        extra_kwargs = {'steps': {'required': False},
                        'unit': {'required': False},}


class SolutionSerializer(CreateWithUserInCasestudyMixin,
                         NestedHyperlinkedModelSerializer):
    parent_lookup_kwargs = {
        'casestudy_pk': 'solution_category__keyflow__casestudy__id',
        'keyflow_pk': 'solution_category__keyflow__id',
        'solutioncategory_pk': 'solution_category__id',
    }

    user = UserInCasestudyField(view_name='userincasestudy-detail',
                                read_only=True)
    solution_category = IDRelatedField()
    currentstate_image = serializers.ImageField(required=False, allow_null=True)
    activities_image = serializers.ImageField(required=False, allow_null=True)
    effect_image = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = Solution
        fields = ('url', 'id', 'name', 'user', 'description',
                  'documentation', 'solution_category',
                  'activities_image',
                  'currentstate_image', 'effect_image'
                  )
        read_only_fields = ('url', 'id', )
        extra_kwargs = {
            'possible_implementation_area': {
                'allow_null': True,
                'required': False,
            },
            'description': {'required': False},
            'documentation': {'required': False},
        }


class SolutionPartSerializer(CreateWithUserInCasestudyMixin,
                             NestedHyperlinkedModelSerializer):
    solution = IDRelatedField(read_only=True)
    parent_lookup_kwargs = {
        'casestudy_pk': 'solution__solution_category__keyflow__casestudy__id',
        'keyflow_pk': 'solution__solution_category__keyflow__id',
        'solutioncategory_pk': 'solution__solution_category__id',
        'solution_pk': 'solution__id'
    }

    # ToDo: serialize affected flows as part of this serializer

    class Meta:
        model = SolutionPart
        fields = ('url', 'id', 'solution', 'documentation',
                  'implements_new_flow',
                  'implementation_flow_origin_activity',
                  'implementation_flow_destination_activity',
                  'implementation_flow_material',
                  'implementation_flow_process',
                  'implementation_flow_spatial_application',
                  'implementation_question', 'a', 'b',
                  'keep_origin', 'new_target', 'map_request',
                  'priority'
                  )
        read_only_fields = ('url', 'id', 'solution')
        extra_kwargs = {
            'implementation_question': {'null': True, 'required': False},
            'keep_origin': {'required': False},
            'new_target': {'required': False},
            'map_request': {'required': False},
            'documentation': {'required': False}
        }
