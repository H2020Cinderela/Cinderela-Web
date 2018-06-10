from django.contrib.gis.geos import Point, LineString

import factory
from factory.django import DjangoModelFactory
from repair.apps.login.factories import CaseStudyFactory

from . import models


class VertexFactory(DjangoModelFactory):
    class Meta:
        model = models.Vertex
    casestudy = 7
    vertex_id = 9999
    geom = Point(x=11.1, y=12.2, srid=4326)


class EdgeFactory(DjangoModelFactory):
    class Meta:
        model = models.Edge
    casestudy = 7
    edge_id = 8888
    fromnode = factory.SubFactory(VertexFactory)
    tonode = factory.SubFactory(VertexFactory)
    geom = LineString(Point(1, 1), Point(2, 2), srid=4326)
