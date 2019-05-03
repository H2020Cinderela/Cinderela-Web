from django.utils.translation import ugettext_lazy as _
from rest_framework_nested.serializers import NestedHyperlinkedModelSerializer
from rest_framework import serializers

from repair.apps.asmfa.graphs.graph import StrategyGraph
from repair.apps.changes.models import (Strategy,
                                        SolutionInStrategy,
                                        ImplementationQuantity,
                                        ActorInSolutionPart
                                        )

from repair.apps.login.serializers import (InCasestudyField,
                                           UserInCasestudyField,
                                           InCaseStudyIdentityField,
                                           IdentityFieldMixin,
                                           CreateWithUserInCasestudyMixin,
                                           IDRelatedField)


class SolutionInStrategySetField(InCasestudyField):
    """Returns a list of links to the solutions"""
    lookup_url_kwarg = 'strategy_pk'
    parent_lookup_kwargs = {
        'casestudy_pk': 'strategy__keyflow__casestudy__id',
        'keyflow_pk': 'strategy__keyflow__id',
        'strategy_pk': 'strategy__id'
    }


class SolutionIISetField(InCasestudyField):
    """Returns a list of links to the solutions"""
    parent_lookup_kwargs = {
        'casestudy_pk': 'keyflow__casestudy__id',
        'keyflow_pk': 'keyflow__id',
        'solutioncategory_pk': 'id'
    }


class SolutionInStrategyListField(IdentityFieldMixin,
                                  SolutionInStrategySetField):
    """Returns a Link to the solutions--list view"""
    parent_lookup_kwargs = {
        'casestudy_pk': 'keyflow__casestudy__id',
        'keyflow_pk': 'keyflow__id',
        'strategy_pk': 'id'
    }


class StakeholderOfStrategyField(InCasestudyField):
    parent_lookup_kwargs = {
        'casestudy_pk': 'stakeholder_category__casestudy__id',
        'stakeholdercategory_pk': 'stakeholder_category__id', }


class StrategySerializer(CreateWithUserInCasestudyMixin,
                         NestedHyperlinkedModelSerializer):
    parent_lookup_kwargs = {
        'casestudy_pk': 'keyflow__casestudy__id',
        'keyflow_pk': 'keyflow__id',
    }
    solution_list = SolutionInStrategyListField(
        source='solutioninstrategy_set',
        view_name='solutioninstrategy-list')
    sii_set = SolutionInStrategySetField(
        source='solutioninstrategy_set',
        view_name='solutioninstrategy-detail',
        many=True,
        read_only=True)
    coordinating_stakeholder = IDRelatedField()
    user = IDRelatedField(read_only=True)
    graph_build = serializers.SerializerMethodField()

    class Meta:
        model = Strategy
        fields = ('url', 'id', 'name', 'user',
                  'coordinating_stakeholder',
                  'solution_list',
                  'sii_set',
                  'graph_build'
                  )

    def get_graph_build(self, obj):
        sgraph = StrategyGraph(obj)
        return sgraph.date

    def update(self, instance, validated_data):
        """
        update the strategy-attributes,
        including selected solutions
        """
        strategy = instance

        # handle solutions
        new_solutions = validated_data.pop('solutions', None)
        if new_solutions is not None:
            SolutionInStrategyModel = Strategy.solutions.through
            solution_qs = SolutionInStrategyModel.objects.filter(
                strategy=strategy)
            # delete existing solutions
            solution_qs.exclude(solution_id__in=(
                sol.id for sol in new_solutions)).delete()
            # add or update new solutions
            for sol in new_solutions:
                SolutionInStrategyModel.objects.update_or_create(
                    strategy=strategy,
                    solution=sol)

        # update other attributes
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class StrategyField(InCasestudyField):
    parent_lookup_kwargs = {
        'casestudy_pk': 'strategy__keyflow__casestudy__id',
        'keyflow_pk': 'strategy__keyflow__id'
    }


class ImplementationQuantitySerializer(serializers.ModelSerializer):
    class Meta:
        model = ImplementationQuantity
        fields = ('question', 'value')


class ActorInSolutionPartSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActorInSolutionPart
        fields = ('solutionpart', 'actor')


class SolutionInStrategySerializer(serializers.ModelSerializer):
    parent_lookup_kwargs = {
        'casestudy_pk': 'strategy__keyflow__casestudy__id',
        'keyflow_pk': 'strategy__keyflow__id',
        'strategy_pk': 'strategy__id'
    }
    participants = IDRelatedField(many=True, required=False)
    quantities = ImplementationQuantitySerializer(
        many=True, source='implementation_quantity', required=False)
    picked_actors = ActorInSolutionPartSerializer(many=True, required=False)

    class Meta:
        model = SolutionInStrategy
        fields = ('id', 'solution', 'note', 'geom',
                  'participants', 'priority', 'quantities', 'picked_actors')

    def update(self, instance, validated_data):
        quantities = validated_data.pop('implementation_quantity', [])
        picked_actors = validated_data.pop('picked_actors', None)
        instance = super().update(instance, validated_data)
        for q in quantities:
            # quantities are created automatically, no need to delete them
            quantity = ImplementationQuantity.objects.get(
                question=q['question'], implementation=instance)
            quantity.value = q['value'];
            quantity.save()
        if picked_actors:
            ActorInSolutionPart.objects.filter(implementation=instance).delete()
            for a in picked_actors:
                ais = ActorInSolutionPart(implementation=instance, **a)
                ais.save()
        return instance

