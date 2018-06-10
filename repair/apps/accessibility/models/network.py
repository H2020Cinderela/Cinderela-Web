
from django.contrib.gis.db import models

from repair.apps.login.models import (GDSEUniqueNameModel, CaseStudy)

from repair.apps.utils.protect_cascade import PROTECT_CASCADE


class Vertex(models.Model):
    casestudy = models.IntegerField()
    vertex_id = models.BigIntegerField()
    cnt = models.IntegerField(null=True)
    chk = models.IntegerField(null=True)
    ein = models.IntegerField(null=True)
    eout = models.IntegerField(null=True)
    geom = models.PointField(blank=False, null=False)


class Edge(models.Model):
    casestudy = models.IntegerField()
    edge_id = models.IntegerField()
    fromnode = models.ForeignKey(Vertex,
                                 on_delete=models.DO_NOTHING,
                                 related_name='fromnode')
    tonode = models.ForeignKey(Vertex,
                               on_delete=models.DO_NOTHING,
                               related_name='tonode')
    geom = models.LineStringField(blank=False, null=False)
    source = models.IntegerField(null=True)
    target = models.IntegerField(null=True)
    cost = models.FloatField(null=True)
    reverse_cost = models.FloatField(null=True)
