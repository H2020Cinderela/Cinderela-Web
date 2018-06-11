
from django.test import TestCase
from django.contrib.gis.geos import Point, LineString

from django.db import connections

from repair.apps.accessibility.models import Vertex, Edge
from repair.apps.accessibility.factories import (VertexFactory,
                                                 EdgeFactory)



class NetworkTest(TestCase):

    @classmethod
    def setUpClass(cls):
        """Build Test network"""
        super().setUpClass()
        N = 5
        cls.N = N
        casestudy = 7
        cls.casestudy = casestudy
        print('create vertices')
        # create N*N vertices
        for x in range(N):
            for y in range(N):
                vertex_id = x * N + y
                vertex = VertexFactory(casestudy=casestudy,
                                       vertex_id=vertex_id,
                                       geom=Point(x, y, srid=4326))
                vertex.save()

        # create edges
        print('create edges')
        edge_id = 1
        for x1 in range(N):
            for y1 in range(N):
                vertex_id1 = x1 * N + y1
                vertex1 = Vertex.objects.get(vertex_id=vertex_id1)
                for diff in ((0, 1), (1, 0), (1, 1)):
                    dx, dy = diff
                    x2 = x1 + dx
                    y2 = y1 + dy
                    if x2 >= N or y2 >= N:
                        continue
                    vertex_id2 = x2 * N + y2
                    vertex2 = Vertex.objects.get(vertex_id=vertex_id2)

                    edge = EdgeFactory(casestudy=casestudy,
                                       edge_id=edge_id,
                                       source=vertex1.vertex_id,
                                       target=vertex2.vertex_id,
                                       geom=LineString(vertex1.geom,
                                                       vertex2.geom,
                                                       srid=4326),
                                       fromnode=vertex1,
                                       tonode=vertex2,
                                       )
                    edge.cost = edge.geom.length
                    edge.reverse_cost = edge.cost
                    edge.save()
                    edge_id += 1

    def test_isochrone(self):
        max_dist = 4.0
        assert isinstance(self.casestudy, int)
        vertex = Vertex.objects.get(pk=7)
        sql = \
'''
CREATE OR REPLACE VIEW isochrones_test AS
SELECT d.node::integer AS id,
d.agg_cost AS cost,
st_x(n.geom)::double precision AS x,
st_y(n.geom)::double precision AS y
FROM pgr_drivingDistance(
'SELECT id, source, target, reverse_cost as cost, cost as reverse_cost
 FROM accessibility_edge
 WHERE casestudy={cs}'::text,
%s, %s::float, true
) d,
accessibility_vertex n
WHERE d.node = n.id;'''.format(cs=self.casestudy)

        connection = connections['accessibility_db']
        with connection.cursor() as cursor:
            res = cursor.execute(sql, (vertex.vertex_id,
                                       max_dist))

        sql = \
'''
SELECT 3 AS cutoff,
ST_AsGeoJSON(pgr_pointsAsPolygon(
  'SELECT id, x, y FROM isochrones_test WHERE cost < 3 '::text),
  7, 3) AS json
UNION
SELECT 4 AS cutoff,
ST_AsGeoJSON(pgr_pointsAsPolygon(
'SELECT id, x, y FROM isochrones_test WHERE cost < 4 '::text),
  7, 3) AS json
'''
        with connection.cursor() as cursor:
            cursor.execute(sql)
            rows = cursor.fetchall()
        print(rows)
