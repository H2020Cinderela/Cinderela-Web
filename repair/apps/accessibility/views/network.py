from repair.apps.login.views import CasestudyViewSetMixin
from repair.apps.accessibility.models import Vertex, Edge
from repair.apps.accessibility.serializers import (VertexSerializer,
                                                   EdgeSerializer)
from repair.apps.utils.views import ModelPermissionViewSet


class VertexViewset(CasestudyViewSetMixin, ModelPermissionViewSet):
    serializer_class = VertexSerializer
    queryset = Vertex.objects.all()


class EdgeViewset(CasestudyViewSetMixin, ModelPermissionViewSet):
    serializer_class = EdgeSerializer
    queryset = Edge.objects.all()

