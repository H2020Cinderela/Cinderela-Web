# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.contrib.gis.db import models as gis

from repair.apps.studyarea.models import Area
from .nodes import Actor


class Geolocation(gis.Model):

    country_choices = (("NL", "The Netherlands"),
                       ("IT", "Italy"),
                       ("PL", "Poland"),
                       ("DE", "Germany"),
                       ("BE", "Belgium"),
                       ("HU", "Hungary"),
                       ("SB", "Sandbox"),
                       ("EU", "European Union"),
                       ("-1", "Outside EU"))

    name = models.TextField(blank=True, null=True)
    postcode = models.CharField(max_length=10, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    country = models.CharField(max_length=255, choices=country_choices,
                               default="-1")
    city = models.CharField(max_length=255, blank=True, null=True)
    geom = gis.PointField(blank=True, null=True)
    area = models.ForeignKey(Area, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        ret = '{s}@({g})'.format(s=self.address, g=self.geom)
        return ret

    class Meta:
        abstract = True
        
    @property
    def level(self):
        """Return the adminlevel of the area, if exists, else None"""
        return getattr(self.area, 'adminlevel_id', None)


class Establishment(Geolocation):

    @property
    def casestudy(self):
        return self.actor.activity.activitygroup.keyflow.casestudy

    @property
    def keyflow(self):
        return self.actor.activity.activitygroup.keyflow

    class Meta(Geolocation.Meta):
        abstract = True


class AdministrativeLocation(Establishment):
    """Administrative Location of Actor"""
    actor = models.OneToOneField(Actor,
                                 null=True,
                                 related_name='administrative_location',
                                 on_delete=models.CASCADE)


class OperationalLocation(Establishment):
    """Operational Location of Actor"""
    actor = models.ForeignKey(Actor,
                              related_name='operational_locations',
                              on_delete=models.CASCADE)
