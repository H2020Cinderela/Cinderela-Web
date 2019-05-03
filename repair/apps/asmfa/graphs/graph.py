from repair.apps.asmfa.models import (Actor2Actor, FractionFlow, Actor,
                                      ActorStock, Material,
                                      StrategyFractionFlow)
from repair.apps.asmfa.graphs.graphwalker import GraphWalker
import graph_tool as gt
from graph_tool import stats as gt_stats
from django.db.models import Q
import numpy as np
import datetime
import cairo
from io import StringIO
from django.conf import settings
import os
from datetime import datetime
from itertools import chain


class BaseGraph:
    def __init__(self, keyflow):
        self.keyflow = keyflow
        self.graph = None

    @property
    def path(self):
        path = settings.GRAPH_ROOT
        cspath = os.path.join(
            path, "casestudy-{}".format(self.keyflow.casestudy.id))
        if not os.path.exists(cspath):
            os.makedirs(cspath)
        return cspath

    @property
    def filename(self):
        fn = "keyflow-{}-base.gt".format(self.keyflow.id)
        return os.path.join(self.path, fn)

    @property
    def date(self):
        if not self.exists:
            return None
        t = os.path.getmtime(self.filename)
        return datetime.utcfromtimestamp(t).strftime('%Y-%m-%d %H:%M:%S')

    @property
    def exists(self):
        return os.path.exists(self.filename)

    def load(self):
        self.graph = gt.load_graph(self.filename)
        return self.graph

    def save(self, graph=None):
        graph = graph or self.graph
        self.graph.save(self.filename)

    def build(self):
        actorflows = FractionFlow.objects.filter(keyflow=self.keyflow, to_stock=False)
        # BD: getting confused with using FractionFlow and Actor2Actor
        # actorflows = Actor2Actor.objects.filter(keyflow=self.keyflow)
        stockflows = FractionFlow.objects.filter(keyflow=self.keyflow, to_stock=True)
        actors = Actor.objects.filter(
            Q(id__in=actorflows.values('origin_id')) |
            Q(id__in=actorflows.values('destination_id')) |
            Q(id__in=stockflows.values('origin_id'))
        )
        flows = list(chain(actorflows, stockflows))

        self.graph = gt.Graph(directed=True)

        # Add the actors to the graph
        self.graph.add_vertex(len(actors))
        self.graph.vertex_properties["id"] = \
            self.graph.new_vertex_property("int")
        self.graph.vertex_properties["bvdid"] = \
            self.graph.new_vertex_property("string")
        self.graph.vertex_properties["name"] = \
            self.graph.new_vertex_property("string")

        actorids = {}
        for i in range(len(actors)):
            self.graph.vp.id[i] = actors[i].id
            self.graph.vp.bvdid[i] = actors[i].BvDid
            self.graph.vp.name[i] = actors[i].name
            actorids[actors[i].id] = i

        # Add the flows to the graph
        # need a persistent edge id, because graph-tool can reindex the edges
        self.graph.edge_properties["id"] = self.graph.new_edge_property("int")
        self.graph.edge_properties['amount'] = self.graph.new_edge_property("int")
        self.graph.edge_properties['material'] = self.graph.new_edge_property("string")

        for i in range(len(flows)):
            # get the start and and actor id's
            flow = flows[i]
            v0 = actorids.get(flow.origin.id)
            if not flow.to_stock:
                v1 = actorids.get(flow.destination.id)
            else:
                v1 = v0

            if (v0 != None and v1 != None and isinstance(flows[i], FractionFlow)):
                e = self.graph.add_edge(
                    self.graph.vertex(v0), self.graph.vertex(v1))
                self.graph.ep.id[e] = flows[i].id
                self.graph.ep.material[e] = flows[i].material
                self.graph.ep.amount[e] = flows[i].amount

        self.save()
        # save graph image
        #pos = gt.draw.fruchterman_reingold_layout(g, n_iter=1000)
        #gt.draw.graph_draw(g, pos, vertex_size=20, vertex_text=g.vp.name,
        #                       vprops={"text_position":0, "font_weight": cairo.FONT_WEIGHT_BOLD, "font_size":14},
        #                       output_size=(700,600), output="test.png")
        return self.graph

    def validate(self):
        """Validate flows for a graph"""
        invalid = []
        self.load()

        for v in self.graph.vertices():
            if(len(v.all_edges()) == 0):
                invalid.append(v)

        if len(invalid) != 0:
            return invalid
        else:
            return 'Graph is valid'

    def serialize(self):
        flows = []
        if not self.graph:
            self.load()
        for e in self.graph.edges():
            flow = {}
            flow['id'] = self.graph.ep.id[e]
            flow['source'] = self.graph.vp.id[e.source()]
            flow['target'] = self.graph.vp.id[e.target()]
            flow['material'] = self.graph.ep.material[e]
            flow['amount'] = self.graph.ep.amount[e]
            flows.append(flow)
        return {'flows':flows}


class StrategyGraph(BaseGraph):
    def __init__(self, strategy):
        self.keyflow = strategy.keyflow
        self.strategy = strategy

    @property
    def filename(self):
        fn = "keyflow-{}-s{}.gt".format(self.keyflow.id, self.strategy.id)
        return os.path.join(self.path, fn)

    def build(self):
        base_graph = BaseGraph(self.keyflow)
        if not base_graph.exists:
            raise FileNotFoundError
        g = base_graph.load()
        gw = GraphWalker(g)
        # ToDo: remove,
        # atm returns the base graph, because the following code is only pseudo
        return g;

        # @Tom or @Balasz: please implement the pseudo-code below!

        # ToDo: get the solutions in this strategy and order them by
        # priority
        for solution in solutions:
            # ToDo: get the solution part
            for solution_part in solution_parts:
                # ToDo: get the implementation and its quantity
                # ToDo: SolutionInStrategy geometry for filtering?
                self.graph = gw.calculate_solution(solution, solution_part,
                                                   quantity)
        self.graph.save(self.filename)

        # ToDo: wipe all existing StrategyFractionFlows with strategy id
        # (modified ones) and FractionFlows with strategy id (new ones)
        self.clean()

        # ToDo: put modifications and new flows into database
        self.translate_to_db()
        return self.graph

    def clean(self):
        flows = FractionFlow.objects.filter(strategy=self.strategy)
        flows.destroy() # or sth like that
        modified = StrategyFractionFlow.objects.filter(strategy=self.strategy)
        modified.destroy()

    def translate_to_db(self):

        # ToDo: get edges from self.graph with no fractionflow id
        for edge in edges:
            origin = Actor.objects.get(edge.originid)
            new_flow = FractionFlow(origin=origin, destination=destination,
                                    amount=edge.amount,
                                    strategy=self.strategy,
                                    # ToDo: all other attributes like material,
                                    # maybe get some of those from the flow the
                                    # new edge was derived from
                                    )

        # ToDo: get modified flows from self.graph:
        for edge in modified_edges:
            mod_flow = StrategyFractionFlow(fractionflow=edge.fractionflowid,
                                            amount=edge.amount,
                                            strategy=self.strategy)

        # ToDo: deleted flows? keep track of those (ids are sufficient) somehow
        # or set amounts to zero in graph instead of actual deleting (then you
        # don't need this part, the one before would deal with it)
        for del_id in deleted_flow_ids:
            mod_flow = StrategyFractionFlow(fractionflow=del_id,
                                            amount=0,
                                            strategy=self.strategy)

    def to_queryset(self):
        if not self.graph:
            self.load()

        for e in self.graph.edges():
            flow = {}
            flow['id'] = self.graph.ep.id[e]
            flow['source'] = self.graph.vp.id[e.source()]
            flow['target'] = self.graph.vp.id[e.target()]
            flow['material'] = self.graph.ep.material[e]
            flow['amount'] = self.graph.ep.amount[e]
            flows.append(flow)