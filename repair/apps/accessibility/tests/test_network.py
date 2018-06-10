
from django.test import TestCase
from django.urls import reverse
from test_plus import APITestCase
from repair.tests.test import BasicModelPermissionTest

from repair.apps.accessibility.factories import (VertexFactory,
                                                 EdgeFactory)



class NetworkTest(TestCase):

    def test_vertex(self):
        vertex = VertexFactory()
        print(vertex)

    def test_edge(self):
        edge = EdgeFactory()
        print(edge)