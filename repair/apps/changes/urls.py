from django.conf.urls import url

from repair.apps.changes import views

urlpatterns = [
    url(r'^$', views.index, name='index'),

    # ex: /casestudy/5/
    url(r'^(?P<casestudy_id>[0-9]+)/$',
        views.casestudy,
        name='casestudy'),

    # ex: /stakeholdercategories/3
    url(r'^stakeholdercategories/(?P<stakeholder_category_id>[0-9]+)/$',
        views.stakeholder_categories,
        name='stakeholder_categories'),

    # ex: /stakeholders/3
    url(r'^stakeholders/(?P<stakeholder_id>[0-9]+)/$',
        views.stakeholders,
        name='stakeholders'),

    # ex: /implementations/3
    url(r'^implementations/(?P<implementation_id>[0-9]+)/$',
        views.implementations,
        name='implementations'),

    # ex: /solutions/3
    url(r'^solutions/(?P<solution_id>[0-9]+)/$',
        views.solutions,
        name='solutions'),

    # ex: /implementations/3/solutions/2
    url(r'^implementations/(?P<implementation_id>[0-9]+)/solutions/(?P<solution_id>[0-9]+)/$',
        views.solution_in_implematation,
        name='solution_in_implementation'),

    # ex: /strategies/3/
    url(r'^strategies/(?P<strategy_id>[0-9]+)/$',
        views.strategies,
        name='strategies'),

    # ex: /users12/3/
    url(r'^users12/(?P<user_id>[0-9]+)/$',
        views.user12,
        name='user12'),

    # ex: /users34/3/
    url(r'^users34/(?P<user_id>[0-9]+)/$',
        views.user34,
        name='user34'),

]