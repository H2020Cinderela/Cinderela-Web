# -*- coding: utf-8 -*-

import json
import geojson
from django.urls import reverse
from django.contrib.gis import geos
from django.core.exceptions import FieldError
from test_plus import APITestCase
from rest_framework import status

import repair.apps.studyarea.models as models
from repair.apps.login.factories import CaseStudyFactory
from repair.tests.test import LoginTestCase, CompareAbsURIMixin


class AreaModelsTest(LoginTestCase, APITestCase):
    @classmethod
    def setUpClass(cls):
        super(AreaModelsTest, cls).setUpClass()
        # create a casestudy
        casestudy = cls.uic.casestudy

        adminlevels = models.AdminLevels.objects
        cls.planet = adminlevels.create(name='Planet',
                                        level=1,
                                        casestudy=casestudy)
        cls.continent = adminlevels.create(name='Continent',
                                           level=2,
                                           casestudy=casestudy)
        cls.country = adminlevels.create(name='Country',
                                         level=3,
                                         casestudy=casestudy)
        cls.land = adminlevels.create(name='Province',
                                      level=4,
                                      casestudy=casestudy)


    def test_01_dynamic_models(self):

        world = self.planet.create_area(name='Earth')
        eu = self.continent.create_area(name='EU')
        spain = self.country.create_area(name='ES')
        de = self.country.create_area(name='DE')
        hh = self.land.create_area(name='Hamburg')
        catalunia = self.land.create_area(name='Catalunia')
        castilia = self.land.create_area(name='Castilia')

        eu.parent_area = world
        spain.parent_area = eu
        de.parent_area = eu
        hh.parent_area = de
        castilia.parent_area = spain
        catalunia.parent_area = eu

        eu.save()
        spain.save()
        de.save()
        hh.save()
        castilia.save()
        catalunia.save()

        areas = models.Area.objects.all()
        assert areas.count() == 7

        self.assertSetEqual(set(eu.area_set.filter(adminlevel__level=3)),
                            {spain, de})
        self.assertSetEqual(set(eu.area_set.filter(adminlevel__level=4)),
                            {catalunia})
        self.assertSetEqual(set(spain.area_set.filter(adminlevel__level=4)),
                            {castilia})

        self.assertEqual(models.Area.objects.get(name='ES'), spain)


class AdminLevelsTest(LoginTestCase, CompareAbsURIMixin, APITestCase):

    @classmethod
    def setUpClass(cls):
        super(AdminLevelsTest, cls).setUpClass()
        # create a casestudy
        casestudy = cls.uic.casestudy

        planet = models.AdminLevels.objects.create(name='Planet',
                                                   level=1,
                                                   casestudy=casestudy)
        land = models.AdminLevels.objects.create(name='Bundesland',
                                                 level=4,
                                                 casestudy=casestudy)
        kreis = models.AdminLevels.objects.create(name='Kreis',
                                                  level=6,
                                                  casestudy=casestudy)
        amt = models.AdminLevels.objects.create(name='Amt',
                                                level=7,
                                                casestudy=casestudy)
        gemeinde = models.AdminLevels.objects.create(
            name='Gemeinde',
            level=8,
            casestudy=casestudy
        )
        ortsteil = models.AdminLevels.objects.create(
            name='Ortsteil',
            level=10,
            casestudy=casestudy)

        cls.casestudy = casestudy
        cls.kreis = kreis
        cls.gemeinde = gemeinde
        cls.ortsteil = ortsteil

        world = models.Area.objects.create(name='Earth',
                                           adminlevel=planet)

        saturn = models.Area.objects.create(name='Saturn',
                                            adminlevel=planet)

        hh = models.Area.objects.create(name='Hamburg',
                                        parent_area=world,
                                        adminlevel=land)
        sh = models.Area.objects.create(name='Schleswig-Holstein',
                                         parent_area=world,
                                         adminlevel=land,
                                         code='iamcode')
        kreis_pi = models.Area.objects.create(
            name='Kreis PI',
            parent_area=sh,
            adminlevel=kreis)
        elmshorn = models.Area.objects.create(
            name='Elmshorn',
            parent_area=kreis_pi,
            adminlevel=gemeinde)
        pinneberg = models.Area.objects.create(
            name='Pinneberg',
            parent_area=kreis_pi,
            adminlevel=gemeinde)
        amt_pinnau = models.Area.objects.create(
            name='Amt Pinnau',
            parent_area=kreis_pi,
            adminlevel=amt)
        ellerbek = models.Area.objects.create(
            name='Ellerbek',
            parent_area=amt_pinnau,
            adminlevel=gemeinde)
        schnelsen = models.Area.objects.create(
            name='Schnelsen',
            parent_area=hh,
            adminlevel=ortsteil)
        burgwedel = models.Area.objects.create(
            name='Burgwedel',
            parent_area=hh,
            adminlevel=ortsteil)
        egenbuettel = models.Area.objects.create(
            name='Egenbüttel',
            parent_area=ellerbek,
            adminlevel=ortsteil)
        langenmoor = models.Area.objects.create(
            name='Langenmoor',
            parent_area=elmshorn,
            adminlevel=ortsteil)
        elmshorn_mitte = models.Area.objects.create(
            name='Elmshorn-Mitte',
            parent_area=elmshorn,
            adminlevel=ortsteil)

        cls.kreis_pi = kreis_pi
        cls.elmshorn = elmshorn
        cls.sh = sh

    @classmethod
    def tearDownClass(cls):
        del cls.casestudy
        del cls.kreis
        del cls.gemeinde
        del cls.ortsteil
        del cls.kreis_pi
        super().tearDownClass()

    def test_get_levels(self):
        """Test the list of all levels of a casestudy"""

        casestudy = self.casestudy
        kreis = self.kreis

        # define the urls
        response = self.get_check_200('adminlevels-list',
                                      casestudy_pk=casestudy.pk)
        data = response.data['results']
        assert data[2]['name'] == kreis.name
        assert data[2]['level'] == kreis.level

    def test_get_gemeinden_of_casestudy(self):
        """Test the list of all areas of a certain level of a casestudy"""

        casestudy = self.casestudy

        response = self.get_check_200('adminlevels-detail',
                                      casestudy_pk=casestudy.pk,
                                      pk=self.gemeinde.pk)
        assert response.data['name'] == 'Gemeinde'
        level_area = response.data['level']

        # define the urls
        response = self.get_check_200('area-list',
                                      casestudy_pk=casestudy.pk,
                                      level_pk=self.gemeinde.pk)
        data = response.data['results']
        self.assertSetEqual({a['name'] for a in data},
                            {'Pinneberg', 'Elmshorn', 'Ellerbek'})

    def test_get_ortsteile_of_kreis(self):
        """
        Test the list of all ortsteile of a kreis with
        an additional filter
        """
        casestudy = self.casestudy
        # get the admin levels
        response = self.get_check_200('adminlevels-list',
                                      casestudy_pk=casestudy.pk)
        data = response.data

        # define the urls
        response = self.get_check_200('area-list',
                                      casestudy_pk=casestudy.pk,
                                      level_pk=self.ortsteil.pk,
                                      data={  #'parent_level': 6,
                                            'parent_area': self.elmshorn.id,})

        assert response.status_code == status.HTTP_200_OK
        data = response.data['results']

        self.assertSetEqual({a['name'] for a in data},
                            {'Langenmoor', 'Elmshorn-Mitte'})

        # test if we can use lookups like name__istartswith
        response = self.get_check_200('area-list',
                                      casestudy_pk=casestudy.pk,
                                      level_pk=self.ortsteil.pk,
                                      data={'parent_level': 6,
                                            'parent_id': self.kreis_pi.pk,
                                            'name__istartswith': 'e',})

        #this should return all ortsteile starting with an 'E'
        self.assertSetEqual({a['name'] for a in response.data['results']},
                           {'Egenbüttel', 'Elmshorn-Mitte'})

    def test_add_geometry(self):
        """Test adding a geometry to an area"""
        response = self.get_check_200('area-detail',
                                      casestudy_pk=self.casestudy.pk,
                                      level_pk=self.kreis_pi.adminlevel.pk,
                                      pk=self.kreis_pi.pk)
        data = response.data
        self.assertEqual(data['type'], 'Feature')
        properties = data['properties']
        cs_uri = self.reverse('casestudy-detail', pk=self.casestudy.pk)
        level_uri = self.reverse('adminlevels-detail',
                                 casestudy_pk=self.casestudy.pk,
                                 pk=self.kreis_pi.adminlevel.pk)
        self.assertURLEqual(properties['casestudy'], cs_uri)
        self.assertURLEqual(properties['adminlevel'], level_uri)
        assert properties['name'] == self.kreis_pi.name

        # geometry is None
        assert data['geometry'] is None

        # add new Polygon as geometry

        polygon = geos.Polygon(((0, 0), (0, 10), (10, 10), (0, 10), (0, 0)),
                               ((4, 4), (4, 6), (6, 6), (6, 4), (4, 4)),
                               srid=4326)

        # and change the name
        new_name = 'Kreis Pinneberg-Elmshorn'
        data = {'geometry': polygon.geojson,
                'properties': {'name': new_name,},}
        response = self.patch('area-detail',
                              casestudy_pk=self.casestudy.pk,
                              level_pk=self.kreis_pi.adminlevel.pk,
                              pk=self.kreis_pi.pk,
                              data=json.dumps(data),
                              extra=dict(content_type='application/json'),
                              )
        self.response_200()
        # test if the new geometry is a multipolygon
        multipolygon = geos.MultiPolygon(polygon)
        self.assertJSONEqual(str(response.data['geometry']),
                                multipolygon.geojson)
        # and that the name has changed
        self.assertEqual(response.data['properties']['name'], new_name)

    def test_add_geometries(self):
        """Test adding features as feature collection"""
        response = self.get_check_200('area-list',
                                      casestudy_pk=self.casestudy.pk,
                                      level_pk=self.kreis.pk)
        num_kreise = len(response.data['results'])

        polygon1 = geos.Polygon(((0, 0), (0, 10), (10, 10), (0, 10), (0, 0)))
        polygon2 = geos.Polygon(((4, 4), (4, 6), (6, 6), (6, 4), (4, 4)))
        kreis1 = geojson.Feature(geometry=geojson.loads(polygon1.geojson),
                                 properties={'name': 'Kreis1',
                                             'code': '01001'})
        kreis2 = geojson.Feature(geometry=geojson.loads(polygon2.geojson),
                                 properties={'name': 'Kreis2',
                                             'code': '01002',
                                             'parent_area_code': self.sh.code,})
        kreise = geojson.FeatureCollection([kreis1, kreis2])
        kreise['parent_level'] = str(4)
        self.post('area-list',
                  casestudy_pk=self.casestudy.pk,
                  level_pk=self.kreis.pk,
                  data=kreise,
                  extra=dict(content_type='application/json'),
                  )
        self.response_201()
        k2 = models.Area.objects.get(code='01002')
        k1 = models.Area.objects.get(code='01001')
        assert k2.name == 'Kreis2'
        assert k1.name == 'Kreis1'

        k2 = models.Area.objects.get(code='01002')
        assert k2.name == 'Kreis2'
        assert k2.parent_area == self.sh

        response = self.get_check_200('area-list',
                                      casestudy_pk=self.casestudy.pk,
                                      level_pk=self.kreis.pk)
        assert len(response.data['results']) == num_kreise + 2

        # posting with relating to parents by area code
        # should fail, when parent_level is missing
        del kreise['parent_level']
        self.post('area-list',
                  casestudy_pk=self.casestudy.pk,
                  level_pk=self.kreis.pk,
                  data=kreise,
                  extra=dict(content_type='application/json'),
                  )
        self.response_400()

        # relate to parent by id
        kreis3 = geojson.Feature(geometry=geojson.loads(polygon2.geojson),
                                 properties={'name': 'Kreis3',
                                             'code': '01003',
                                             'parent_area': self.sh.id})
        self.post('area-list',
                  casestudy_pk=self.casestudy.pk,
                  level_pk=self.kreis.pk,
                  data=kreis3,
                  extra=dict(content_type='application/json'),
                  )
        self.response_201()

        k3 = models.Area.objects.get(code='01003')
        assert k3.parent_area == self.sh

        # posting with both parent_area_code and parent_area_id should fail
        # (only one allowed at a time)
        kreis4 = geojson.Feature(geometry=geojson.loads(polygon2.geojson),
                                 properties={'name': 'Kreis4',
                                             'code': '01004',
                                             'parent_area_code': self.sh.code,
                                             'parent_area': 1})
        kreise = geojson.FeatureCollection([kreis4])
        kreise['parent_level'] = str(4)
        self.post('area-list',
                  casestudy_pk=self.casestudy.pk,
                  level_pk=self.kreis.pk,
                  data=kreise,
                  extra=dict(content_type='application/json'),
                  )
        self.response_400()


    def test_add_geometry_with_parent_area(self):
        """Test adding/updating features with parent levels"""
        polygon1 = geos.Polygon(((0, 0), (0, 10), (10, 10), (0, 10), (0, 0)))
        polygon2 = geos.Polygon(((4, 4), (4, 6), (6, 6), (6, 4), (4, 4)))
        kreis1 = geojson.Feature(geometry=geojson.loads(polygon1.geojson),
                                     properties={'name': 'Kreis1',
                                                 'code': '01001',})
        kreis2 = geojson.Feature(geometry=geojson.loads(polygon1.geojson),
                                     properties={'name': 'Kreis2',
                                                 'code': '01002',})
        gem1 = geojson.Feature(geometry=geojson.loads(polygon2.geojson),
                               properties={'name': 'Gemeinde1',
                                           'code': '01002001',
                                           'parent_area_code': \
                                           kreis2['properties']['code'],})
        gem2 = geojson.Feature(geometry=geojson.loads(polygon2.geojson),
                               properties={'name': 'Gemeinde2',
                                           'code': '01001002',
                                           'parent_area_code': \
                                           kreis1['properties']['code'],})
        kreise = geojson.FeatureCollection([kreis1, kreis2])
        self.post('area-list',
                  casestudy_pk=self.casestudy.pk,
                  level_pk=self.kreis.pk,
                  data=kreise,
                  extra=dict(content_type='application/json'),
                  )
        self.response_201()

        gemeinden = geojson.FeatureCollection([gem1, gem2])
        gemeinden['parent_level'] = 6
        self.post('area-list',
                  casestudy_pk=self.casestudy.pk,
                  level_pk=self.gemeinde.pk,
                  data=gemeinden,
                  extra=dict(content_type='application/json',),
                  )
        self.response_201()

        gem1 = models.Area.objects.get(code='01002001')
        assert gem1.parent_area.code == '01002'
        gem2 = models.Area.objects.get(code='01001002')
        assert gem2.parent_area.code == '01001'






