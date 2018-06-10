
from rest_framework_gis.serializers import GeoFeatureModelSerializer

from repair.apps.accessibility.models import Vertex, Edge


class VertexSerializer(GeoFeatureModelSerializer):

    class Meta:
        model = Vertex
        geo_field = 'geom'


class EdgeSerializer(GeoFeatureModelSerializer):

    class Meta:
        model = Edge
        geo_field = 'geom'
