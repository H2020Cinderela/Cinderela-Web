# -*- coding: utf-8 -*-
from django.db import models
from repair.apps.login.models import (CaseStudy,
                                      GDSEModel, get_default)

from publications_bootstrap.models import (Publication,
                                           Type as PublicationType)


class PublicationInCasestudy(models.Model):
    publication = models.OneToOneField(Publication, on_delete=models.CASCADE)
    casestudy = models.ForeignKey(CaseStudy, on_delete=models.CASCADE)

    def __str__(self):
        return '{} ({})'.format(self.publication, self.casestudy)
