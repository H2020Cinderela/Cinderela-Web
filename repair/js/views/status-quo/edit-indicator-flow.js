define(['views/common/baseview', 'underscore', 'collections/gdsecollection',
        'views/common/flowsankey', 'utils/utils', 'bootstrap-select',
        'bootstrap-tagsinput'],

function(BaseView, _, GDSECollection, FlowSankeyView, utils){
/**
*
* @author Christoph Franke
* @name module:views/IndicatorFlowEditView
* @augments module:views/BaseView
*/
var IndicatorFlowEditView = BaseView.extend(
    /** @lends module:views/FlowsView.prototype */
    {

    /**
    * render view on flow (A or B) settings for indicators
    *
    * @param {Object} options
    * @param {HTMLElement} options.el                     element the view will be rendered in
    * @param {string} options.template                    id of the script element containing the underscore template to render this view
    * @param {module:models/CaseStudy} options.caseStudy  the casestudy to add layers to
    *
    * @constructs
    * @see http://backbonejs.org/#View
    */
    initialize: function(options){
        IndicatorFlowEditView.__super__.initialize.apply(this, [options]);
        _.bindAll(this, 'resetNodeSelects');
        this.activityGroups = options.activityGroups;
        this.activities = options.activities;
        this.materials = options.materials;
        this.caseStudy = options.caseStudy;
        this.keyflowId = options.keyflowId;
        this.indicatorFlow = options.indicatorFlow;

        this.originActors = new GDSECollection([], {
            apiTag: 'actors',
            apiIds: [this.caseStudy.id, this.keyflowId],
            comparator: 'name'
        })
        this.destinationActors = new GDSECollection([], {
            apiTag: 'actors',
            apiIds: [this.caseStudy.id, this.keyflowId],
            comparator: 'name'
        })

        this.render();
    },

    /*
    * dom events (managed by jquery)
    */
    events: {
        'click .render': 'renderSankey'
    },

    render: function(){
        var _this = this;
        var html = document.getElementById(this.template).innerHTML
        var template = _.template(html);
        this.el.innerHTML = template();

        this.showFlowOnlyCheck = this.el.querySelector('input[name="show-flow-only"]');
        this.originSelects = {
            levelSelect: this.el.querySelector('select[name="origin-level-select"]'),
            groupSelect: this.el.querySelector('select[name="origin-group"]'),
            activitySelect: this.el.querySelector('select[name="origin-activity"]'),
            actorSelect: this.el.querySelector('select[name="origin-actor"]')
        }

        this.destinationSelects = {
            levelSelect: this.el.querySelector('select[name="destination-level-select"]'),
            groupSelect: this.el.querySelector('select[name="destination-group"]'),
            activitySelect: this.el.querySelector('select[name="destination-activity"]'),
            actorSelect: this.el.querySelector('select[name="destination-actor"]')
        }

        this.typeSelect = this.el.querySelector('select[name="waste"]');

        $(this.originSelects.groupSelect).selectpicker();
        $(this.originSelects.activitySelect).selectpicker();
        $(this.originSelects.actorSelect).selectpicker();
        $(this.destinationSelects.groupSelect).selectpicker();
        $(this.destinationSelects.activitySelect).selectpicker();
        $(this.destinationSelects.actorSelect).selectpicker();

        this.originSelects.levelSelect.addEventListener(
            'change', function(){ _this.resetNodeSelects('origin') })
        this.destinationSelects.levelSelect.addEventListener(
            'change', function(){ _this.resetNodeSelects('destination') })
        this.showFlowOnlyCheck.addEventListener('change', function(){
            _this.resetNodeSelects('origin'); _this.resetNodeSelects('destination')
        })

        this.addEventListeners('origin');
        this.addEventListeners('destination');
        this.renderMatFilter();

        this.materialTags = this.el.querySelector('input[name="material-tags"]');
        $(this.materialTags).tagsinput({
            itemValue: 'value',
            itemText: 'text'
        })
        // hide the input of tags
        this.materialTags.parentElement.querySelector('.bootstrap-tagsinput>input').style.display = 'none';

        this.setInputs(this.indicatorFlow);
    },

    // filter and fetch the actors by selected group/activity
    // tag indicates the select group ('origin' or 'destination')
    filterActors: function(tag){
        var _this = this,
            geoJSONText,
            queryParams = {
                included: 'True',
                fields: ['id', 'name'].join()
            };

        var selectGroup = (tag == 'origin') ? this.originSelects : this.destinationSelects,
            actors = (tag == 'origin') ? this.originActors : this.destinationActors,
            activity = selectGroup.activitySelect.value,
            group = selectGroup.groupSelect.value;

        if(activity >= 0) queryParams['activity'] = activity;
        else if (group >= 0) queryParams['activity__activitygroup'] = group;

        this.loader.activate({offsetX: '20%'});
        actors.fetch({
            data: queryParams,
            success: function(response){
                _this.loader.deactivate();
                actors.sort();
                _this.renderNodeSelectOptions(selectGroup.actorSelect, actors);
                selectGroup.actorSelect.value = -1;
            },
            reset: true
        })

    },

    // add the event listeners to the group/activity selects
    // tag indicates the select group ('origin' or 'destination')
    addEventListeners: function(tag){
        var _this = this;
        var selectGroup = (tag == 'origin') ? this.originSelects : this.destinationSelects;

        function multiCheck(evt, clickedIndex, checked){
            var select = evt.target;
            if(checked){
                // 'All' clicked -> deselect other options
                if (clickedIndex == 0){
                   $(select).selectpicker('deselectAll');
                    select.value = -1;
                }
                // other option clicked -> deselect 'All'
                else {
                    select.options[0].selected = false;
                }
            }
            // nothing selected anymore -> select 'All'
            if (select.value == null || select.value == ''){
                select.value = -1;
            }
            $(select).selectpicker('refresh');
        }

        $(selectGroup.groupSelect).on('changed.bs.select', function(evt, index, val){
            multiCheck(evt, index, val);
            var level = selectGroup.levelSelect.value;
            if (level == 'group') return;
            var groupId = this.value;
            filteredActivities = (groupId < 0) ? _this.activities:
                _this.activities.filterBy({'activitygroup': groupId});

            _this.renderNodeSelectOptions(selectGroup.activitySelect, filteredActivities);
            if (level == 'actor')
                _this.filterActors(tag);
        })

        $(selectGroup.activitySelect).on('changed.bs.select', function(evt, index, val){
            multiCheck(evt, index, val);
            // nodelevel actor is selected -> filter actors
            if (selectGroup.levelSelect.value == 'actor')
                _this.filterActors(tag);
        })

        $(selectGroup.actorSelect).on('changed.bs.select', multiCheck);
    },

    // reset the options of the selects
    // tag indicates the select group ('origin' or 'destination')
    resetNodeSelects: function(tag){

        var selectGroup = (tag == 'origin') ? this.originSelects : this.destinationSelects,
            level = selectGroup.levelSelect.value,
            hide = [],
            selects = [selectGroup.actorSelect, selectGroup.groupSelect, selectGroup.activitySelect];

        // show the grandparents
        selects.forEach(function(sel){
            sel.parentElement.parentElement.style.display = 'block';
            sel.selectedIndex = 0;
            sel.removeAttribute('multiple');
            sel.style.height ='100%'; // resets size, in case it was expanded
        })
        if (level == 'actor'){
            multi = selectGroup.actorSelect;
        }
        else if (level == 'activity'){
            multi = selectGroup.activitySelect;
            hide = [selectGroup.actorSelect];
        }
        else {
            multi = selectGroup.groupSelect;
            hide = [selectGroup.actorSelect, selectGroup.activitySelect];
        }
        multi.setAttribute('multiple', true);
        $(multi).selectpicker("refresh");
        hide.forEach(function(s){
            s.parentElement.parentElement.style.display = 'none';
        })
        this.renderNodeSelectOptions(selectGroup.groupSelect, this.activityGroups);
        if(level != 'group')
            this.renderNodeSelectOptions(selectGroup.activitySelect, this.activities);
        if(level == 'actor')
            this.renderNodeSelectOptions(selectGroup.actorSelect);

        // selectpicker has to be completely rerendered to change between
        // multiple and single select
        selects.forEach(function(sel){
            $(sel).selectpicker('destroy');
            $(sel).selectpicker();
        });
        // destroying also kills the event listeners
        this.addEventListeners(tag);
    },


    // fill given select with options created based on models of given collection
    renderNodeSelectOptions: function(select, collection){
        var showFlowOnly = this.showFlowOnlyCheck.checked;
        utils.clearSelect(select);
        var defOption = document.createElement('option');
        defOption.value = -1;
        defOption.text = gettext('All');
        if (collection) defOption.text += ' (' + collection.length + ')';
        select.appendChild(defOption);
        var option = document.createElement('option');
        option.dataset.divider = 'true';
        select.appendChild(option);
        if (collection && collection.length < 2000){
            collection.forEach(function(model){
                var flowCount = model.get('flow_count');
                if (showFlowOnly && flowCount == 0) return;
                var option = document.createElement('option');
                option.value = model.id;
                option.text = model.get('name') + ' (' + flowCount + ' ' + gettext('flows') + ')';
                if (flowCount == 0) option.classList.add('empty');
                select.appendChild(option);
            })
            select.disabled = false;
        }
        else {
            defOption.text += ' - ' + gettext('too many to display');
            select.disabled = true;
        }
        select.selectedIndex = 0;
        $(select).selectpicker('refresh');
    },

    // render the material filter
    renderMatFilter: function(){
        var _this = this;
        // select material
        var matSelect = document.createElement('div');
        matSelect.classList.add('materialSelect');
        this.hierarchicalSelect(this.materials, matSelect, {
            onSelect: function(model){
                if (model)
                    $(_this.materialTags).tagsinput('add', {
                        "value": model.id , "text": model.get('name')
                    });
            },
            defaultOption: gettext('Select'),
            label: function(model, option){
                var compCount = model.get('composition_count'),
                    label = model.get('name') + ' (' + compCount + ' ' + gettext('compositions') + ')';
                return label;
            }
        });
        var matFlowless = this.materials.filterBy({'composition_count': 0});
        // grey out materials not used in any flows in keyflow
        // (do it afterwards, because hierarchical select is build in template)
        matFlowless.forEach(function(material){
            var li = matSelect.querySelector('li[data-value="' + material.id + '"]'),
                a = li.querySelector('a');
            a.classList.add('empty');
        })
        this.el.querySelector('.material-filter').appendChild(matSelect);
    },

    // filter section: get the selected nodes of selected level
    getSelectedNodes: function(selectGroup){
        var level = selectGroup.levelSelect.value,
            nodeSelect = (level == 'actor') ? selectGroup.actorSelect:
                         (level == 'activity') ? selectGroup.activitySelect:
                         selectGroup.groupSelect;
        function getValues(selectOptions){
            var values = [];
            for (var i = 0; i < selectOptions.length; i++) {
                var option = selectOptions[i];
                if (option.dataset.divider) continue;
                var id = option.value;
                // ignore 'All' in multi select
                if (id >= 0)
                    values.push(id);
            }
            return values;
        }
        // value will always return the value of the top selected option
        // so if it is > -1 "All" is not selected
        if (nodeSelect.value >= 0){
            selected = nodeSelect.selectedOptions;
            return getValues(selected);
        }
        // "All" is selected -> return values of all options (except "All")
        else return getValues(nodeSelect.options)
    },

    // preset the selected nodes in given select group depending on selected node level
    setSelectedNodes: function(selectGroup, values, actors){
        if (values.length == 0 || values[0].length == 0)
            return;
        var level = selectGroup.levelSelect.value,
            nodeSelect = (level == 'actor') ? selectGroup.actorSelect:
                         (level == 'activity') ? selectGroup.activitySelect:
                         selectGroup.groupSelect,
            _this = this;
        if (level == 'actor') {
            actors.fetch({
                data: {
                    'id__in': values.join(',')
                },
                success: function(){
                    _this.renderNodeSelectOptions(nodeSelect, actors);
                    $(nodeSelect).selectpicker('val', values);
                },
                error: _this.onError
            })
            return;
        }
        $(nodeSelect).selectpicker('val', values);
    },

    // get the selected materials
    selectedMaterials: function(){
        var tags = $(this.materialTags).tagsinput('items'),
            materialIds = [];
        tags.forEach(function(item){
            materialIds.push(item.value)
        })
        return materialIds;
    },

    // preset the selected materials
    setSelectedMaterials: function(materialIds){
        var tags = $(this.materialTags).tagsinput('items'),
            _this = this;
        materialIds.forEach(function(materialId){
            var model = _this.materials.get(materialId);
            $(_this.materialTags).tagsinput('add', {
                "value": model.id , "text": model.get('name')
            });
        });
    },

    // render the sankey diagram
    renderSankey: function(){
        if (this.flowsView != null) this.flowsView.close();
        var el = this.el.querySelector('.sankey-wrapper'),
            originLevel = this.originSelects.levelSelect.value,
            destinationLevel = this.destinationSelects.levelSelect.value,
            _this = this;

        var origins = (originLevel == 'actor') ? this.originActors:
            (originLevel == 'activity') ? this.activities:
            this.activityGroups;
        var destinations = (destinationLevel == 'actor') ? this.destinationActors:
            (destinationLevel == 'activity') ? this.activities:
            this.activityGroups;

        var filterParams = {},
            waste = (this.typeSelect.value == 'waste') ? true :
                    (this.typeSelect.value == 'product') ? false : '';
        if (waste) filterParams.waste = waste;

        var materialIds = this.selectedMaterials();

        if (materialIds.length > 0)
            filterParams.materials = {
                ids: materialIds,
                aggregate: true
            };

        var originNodeIds = this.getSelectedNodes(this.originSelects),
            destinationNodeIds = this.getSelectedNodes(this.destinationSelects);

        var originSuffix = (originLevel == 'activitygroup') ? 'activity__activitygroup__id__in':
                (originLevel == 'activity') ? 'activity__id__in': 'id__in',
            destinationSuffix = (destinationLevel == 'activitygroup') ? 'activity__activitygroup__id__in':
                (destinationLevel == 'activity') ? 'activity__id__in': 'id__in';

        // flow origins and destinations have to be in selected subsets (AND linked, in contrast to FlowsView where you have directions to/from the selected nodes)
        var id_filter = {
                link: 'and',
                functions: []
            }
        if (originNodeIds.length > 0)
            id_filter.functions.push({
                'function': 'origin__' + originSuffix,
                values: originNodeIds
            });

        if (destinationNodeIds.length > 0)
            id_filter.functions.push({
                'function': 'destination__' + destinationSuffix,
                values: destinationNodeIds
            });

        filterParams['filters'] = [id_filter];

        var flows = new GDSECollection([], {
            apiTag: 'actorToActor',
            apiIds: [ this.caseStudy.id, this.keyflowId]
        });

        filterParams['aggregation_level'] = {
            origin: originLevel,
            destination: destinationLevel
        };

        this.loader.activate();
        flows.postfetch({
            body: filterParams,
            success: function(){
                _this.loader.deactivate();
                utils.complementFlowData(flows, origins, destinations,
                    function(origins, destinations){
                        _this.flowsView = new FlowSankeyView({
                            el: el,
                            width:  el.clientWidth - 10,
                            origins: origins,
                            destinations: destinations,
                            flows: flows,
                            materials: _this.materials,
                            hideUnconnected: true,
                            forceSideBySide: true,
                            height: 600
                        })
                    }
                )
            }
        })
    },

    // preset all inputs based on flow data
    setInputs: function(flow){
        var flow = flow || {};
        this.showFlowOnlyCheck.checked = false;
        var materialIds = flow.materials || [],
            originNodeIds = flow.origin_node_ids || "",
            destinationNodeIds = flow.destination_node_ids || "",
            originLevel = flow.origin_node_level || 'activitygroup',
            destinationLevel = flow.destination_node_level || 'activitygroup',
            flowType = flow.flow_type || 'both',
            spatial = flow.spatial_application || 'both';

        this.originSelects.levelSelect.value = originLevel.toLowerCase();
        this.destinationSelects.levelSelect.value = destinationLevel.toLowerCase();
        this.resetNodeSelects('origin');
        this.resetNodeSelects('destination');
        this.setSelectedNodes(this.originSelects, originNodeIds.split(','), this.originActors);
        this.setSelectedNodes(this.destinationSelects, destinationNodeIds.split(','), this.destinationActors);
        this.typeSelect.value = flowType.toLowerCase();
        this.setSelectedMaterials(materialIds);
        this.el.querySelector('input[name="spatial-filtering"][value="' + spatial.toLowerCase() + '"]').checked = true;
    },

    // get the flow with currently set values
    getInputs: function(){
        var materialIds = this.selectedMaterials(),
            originNodeIds = this.getSelectedNodes(this.originSelects),
            destinationNodeIds = this.getSelectedNodes(this.destinationSelects),
            originLevel = this.originSelects.levelSelect.value,
            destinationLevel = this.destinationSelects.levelSelect.value,
            flowType = this.typeSelect.value,
            spatial = this.el.querySelector('input[name="spatial-filtering"]:checked').value;

        var flow = {
            origin_node_level: originLevel,
            origin_node_ids: originNodeIds.join(','),
            destination_node_level: destinationLevel,
            destination_node_ids: destinationNodeIds.join(','),
            materials: materialIds,
            flow_type: flowType,
            spatial_application: spatial
        }

        return flow;
    },

    close: function(){
        if (this.flowsView != null) this.flowsView.close();
        IndicatorFlowEditView.__super__.close.call(this);
    }

});
return IndicatorFlowEditView;
}
);
