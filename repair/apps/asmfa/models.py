# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

from repair.apps.login.models import CaseStudy, Profile, GDSEModel


class DataEntry(models.Model):

    # this I am leaving empty for now - we have to agree at the consortium how we define users and data sources
    user = models.ForeignKey(Profile, default=1)
    source = models.CharField(max_length=255)
    #date =
    pass


class Material(GDSEModel):
    code = models.TextField(unique=True, default='')
    name = models.TextField()
    casestudies = models.ManyToManyField(CaseStudy,
                                         through='MaterialInCasestudy')


class MaterialInCasestudy(models.Model):
    material = models.ForeignKey(Material)
    casestudy = models.ForeignKey(CaseStudy)
    note = models.TextField(default='', blank=True)


class Quality(GDSEModel):
    #material = models.ForeignKey(Material,
                                 #on_delete=models.CASCADE)
    name = models.TextField()


class Geolocation(models.Model):

    # same as for DataEntry, also geometry will have to be included later
    #street =
    #building =
    #postcode =
    #country =
    #city =
    #geom =
    pass


class Node(GDSEModel):  # should there be a separate model for the AS-MFA?

    # all the data for the Node class tables will be known in advance, the users will not have to fill that in
    source = models.BooleanField(default=False)  # if true - there is no input, should be introduced as a constraint later
    sink = models.BooleanField(default=False)  # if true - there is no output, same

    class Meta:
        abstract = True


class ActivityGroup(Node):

    # activity groups are predefined and same for all flows and case studies
    activity_group_choices = (("P1", "Production"),
                              ("P2", "Production of packaging"),
                              ("P3", "Packaging"),
                              ("D", "Distribution"),
                              ("S", "Selling"),
                              ("C", "Consuming"),
                              ("SC", "Selling and Cosuming"),
                              ("R", "Return Logistics"),
                              ("COL", "Collection"),
                              ("W", "Waste Management"),
                              ("imp", "Import"),  # 'import' and 'export' are "special" types of activity groups/activities/actors
                              ("exp", "Export"))
    code = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=255, choices=activity_group_choices)

    casestudy = models.ForeignKey(CaseStudy,
                                  on_delete=models.CASCADE,
                                  default=1)


class Activity(Node):

    nace = models.CharField(max_length=255, unique=True)  # NACE code, unique for each activity
    name = models.CharField(max_length=255)  # not sure about the max length, leaving everywhere 255 for now

    activitygroup = models.ForeignKey(ActivityGroup,
                                      on_delete=models.CASCADE,
                                      default=1)


class Actor(Node):

    BvDid = models.CharField(max_length=255, unique=True) #unique actor identifier in ORBIS database
    name = models.CharField(max_length=255)

    # locations also let's leave out for now, we can add them later
    #operationalLocation = models.ForeignKey('Geolocation', on_delete=models.CASCADE, related_name='operationalLocation')
    #administrativeLocation = models.ForeignKey('Geolocation', on_delete=models.CASCADE, related_name='administrativeLocation')
    consCode = models.CharField(max_length=255)
    year = models.PositiveSmallIntegerField()
    revenue = models.PositiveIntegerField()
    employees = models.PositiveSmallIntegerField()
    BvDii = models.CharField(max_length=255)
    website = models.CharField(max_length=255)

    activity = models.ForeignKey(Activity, on_delete=models.CASCADE,
                                 default=1)


class Flow(models.Model):

    # users will have to add data about flows, that will relate two of the nodes
    # again, there will be limited material and quality choices, we should determine the exact ones later

    amount = models.PositiveIntegerField(blank=True)
    material = models.ForeignKey(MaterialInCasestudy, on_delete=models.CASCADE,
                                 default=13)
    quality = models.ForeignKey(Quality, on_delete=models.CASCADE,
                                default=1)

    class Meta:
        abstract = True


class Group2Group(Flow):

    destination = models.ForeignKey(ActivityGroup, on_delete=models.CASCADE,
                                    related_name='Inputs')
    origin = models.ForeignKey(ActivityGroup, on_delete=models.CASCADE,
                               related_name='Outputs')


class Activity2Activity(Flow):

    destination = models.ForeignKey(Activity, on_delete=models.CASCADE,
                                    related_name='Inputs',
                                    )
    origin = models.ForeignKey(Activity, on_delete=models.CASCADE,
                               related_name='Outputs',
                               )


class Actor2Actor(Flow):

    destination = models.ForeignKey(Actor, on_delete=models.CASCADE,
                                    related_name='Inputs')
    origin = models.ForeignKey(Actor, on_delete=models.CASCADE,
                               related_name='Outputs')


class Stock(models.Model):

    # stocks relate to only one node, also data will be entered by the users
    amount = models.PositiveIntegerField(blank=True)
    material = models.ForeignKey(MaterialInCasestudy, on_delete=models.CASCADE,
                                         default=1)
    quality = models.ForeignKey(Quality, on_delete=models.CASCADE,
                                    default=13)

    class Meta:
        abstract = True


class GroupStock(Stock):

        origin = models.ForeignKey(ActivityGroup, on_delete=models.CASCADE,
                                   related_name='Stocks')


class ActivityStock(Stock):

        origin = models.ForeignKey(Activity, on_delete=models.CASCADE,
                                   related_name='Stocks')


class ActorStock(Stock):

        origin = models.ForeignKey(Actor, on_delete=models.CASCADE,
                                   related_name='Stocks')