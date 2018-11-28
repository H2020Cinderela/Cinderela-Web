define(['views/common/baseview', 'underscore',
        'collections/gdsecollection', 'views/data-entry/edit-actor',
        'datatables.net-bs',
        'datatables.net-bs/css/dataTables.bootstrap.css',
        'datatables.net-buttons-bs/css/buttons.bootstrap.min.css',
        'bootstrap-select'],
function(BaseView, _, GDSECollection, EditActorView){

/**
    *
    * @author Christoph Franke
    * @name module:views/ActorsView
    * @augments module:views/BaseView
    */
var ActorsView = BaseView.extend(
    /** @lends module:views/ActorsView.prototype */
    {

    /**
    * render view to edit the actors of a keyflow
    *
    * @param {Object} options
    * @param {HTMLElement} options.el                     element the view will be rendered in
    * @param {string} options.template                    id of the script element containing the underscore template to render this view
    * @param {module:collections/Keyflows.Model}          options.model the keyflow the actors belong to
    * @param {module:models/CaseStudy} options.caseStudy  the casestudy the keyflow belongs to
    * @param {module:collections/GDSECollection} options.activities  the activities in the keyflow
    *
    * @constructs
    * @see http://backbonejs.org/#View
    */
    initialize: function(options){
        ActorsView.__super__.initialize.apply(this, [options]);
        _.bindAll(this, 'removeActor');
        var _this = this;

        this.template = options.template;
        var keyflowId = this.model.id,
            caseStudyId = this.model.get('casestudy');
        this.activities = options.activities;
        this.actors = new GDSECollection([], {
            apiTag: 'actors',
            apiIds: [ caseStudyId, keyflowId ]
        });
        this.areaLevels = new GDSECollection([], {
            apiTag: 'arealevels',
            apiIds: [ caseStudyId ],
            comparator: 'level'
        });
        this.showAll = true;
        this.caseStudy = options.caseStudy;
        this.caseStudyId = this.model.get('casestudy');

        this.loader.activate();

        this.projection = 'EPSG:4326';

        this.reasons = new GDSECollection([], {
            apiTag: 'reasons'
        });

        Promise.all([
            this.activities.fetch(),
            this.areaLevels.fetch(),
            this.reasons.fetch()
        ]).then(function() {
            _this.areaLevels.sort();
            _this.loader.deactivate();
            _this.render();
        });
    },

    /*
    * dom events (managed by jquery)
    */
    events: {
        'click #remove-actor-button': 'showRemoveModal',
        'click #add-actor-button': 'addActorEvent',
        'change #included-filter-select': 'changeFilter',
        'change select[name="activity-filter"]': 'renderActors'
    },

    /*
    * render the view
    */
    render: function(){
        if (this.activities.length === 0) return;
        var _this = this;
        var html = document.getElementById(this.template).innerHTML
        var template = _.template(html);
        this.el.innerHTML = template({
            casestudy: this.caseStudy.get('properties').name,
            keyflow: this.model.get('name'),
            activities: this.activities
        });
        this.filterSelect = this.el.querySelector('#included-filter-select');
        this.datatable = $('#actors-table').DataTable();
        $('#actors-table tbody').on('click', 'tr', function () {
            _this.selectRow(this);
        });
        this.renderActors();
    },

    renderActors: function(){
        var _this = this,
            activityId = this.el.querySelector('select[name="activity-filter"]').value;
            data = (activityId =="-1") ? {} : { activity: activityId }
        this.datatable.clear().draw();
        this.loader.activate();
        this.actors.fetch({
            data: data,
            success: function(){
                _this.addActorRows(_this.actors);
                _this.loader.deactivate();
            },
            error: function(e){
                _this.loader.deactivate();
                _this.onError(e);
            }
        });
    },

    changeFilter: function(event){
        var _this = this;
        this.showAll = event.target.value == '0';
        if (!this.showAll){
            $.fn.dataTable.ext.search.push(
                function(settings, data, dataIndex) {
                    return $(_this.datatable.row(dataIndex).node()).attr('data-included') == 'true';
                  }
              );
        }
        else $.fn.dataTable.ext.search.pop();
        this.datatable.draw();
    },

    addActorRows: function(actors){
        var _this = this,
            dataRows = [];
        actors.forEach(function(actor){
            row = [
                actor.get('name'),
                actor.get('city'),
                actor.get('address'),
                actor.id
            ];
            var dataRow = _this.datatable.row.add(row);
            dataRows.push(dataRow);
            _this.setIncluded(actor, dataRow);
        });
        this.datatable.draw();
        return dataRows;
    },

    showActor: function(actor, dataRow){
        var _this = this;
        actor.caseStudyId = _this.caseStudy.id;
        actor.keyflowId = _this.model.id;
        _this.activeActor = actor;
        if (_this.actorView != null) _this.actorView.close();
        actor.fetch({ success: function(){
            _this.actorView = new EditActorView({
                el: document.getElementById('edit-actor'),
                template: 'edit-actor-template',
                model: actor,
                activities: _this.activities,
                keyflow: _this.model,
                onUpload: function(a) {
                    _this.setIncluded(a, dataRow);
                    dataRow.data([
                        actor.get('name'),
                        actor.get('city'),
                        actor.get('address')
                    ]);
                    _this.showActor(a, dataRow);
                },
                focusarea: _this.caseStudy.get('properties').focusarea,
                areaLevels: _this.areaLevels,
                reasons: _this.reasons
            });
        }})
    },

    selectRow: function(row){
        var _this = this,
            dataRow = this.datatable.row(row);
        $("#actors-table tbody tr").removeClass('selected');
        row.classList.add('selected');

        var data = dataRow.data(),
            actor = this.actors.get(data[data.length - 1]);
        this.showActor(actor, dataRow);
    },

    setIncluded: function(actor, dataRow){
        var _this = this,
            included = actor.get('included'),
            row = dataRow.node();
        if (!included){
            row.classList.add('dsbld');
            if (!_this.showAll)
                row.style.display = "none";
        } else {
            row.classList.remove('dsbld')
            row.style.display = "table-row";
        }
        row.setAttribute('data-included', included);
    },

    /*
    * add row on button click
    */
    addActorEvent: function(event){
        var _this = this;
        var buttonId = event.currentTarget.id;
        var tableId;

        function onChange(name){
            var actor = _this.actors.create({
                "BvDid": "-",
                "name": name || "-----",
                "consCode": "-",
                "year": null,
                "turnover": null,
                "employees": null,
                "BvDii": "-",
                "website": "www.website.org",
                "activity": _this.activities.first().id,
                'reason': null,
                'description': ''
            }, {
                wait: true,
                success: function(){
                    var dataRow = _this.addActorRows([actor])[0];
                    _this.selectRow(dataRow.node());
                }
            })
        }
        this.getName({
            title: gettext('Add Actor'),
            onConfirm: onChange
        });
    },

    /*
    * show modal for removal on button click
    */
    showRemoveModal: function(){
        if (this.activeActor == null) return;
        var message = gettext('Do you really want to delete the actor') + ' &#60;' + this.activeActor.get('name') + '&#62; ' + '?';
        this.confirm({ message: message, onConfirm: this.removeActor });
    },

    /*
    * remove selected actor on button click in modal
    */
    removeActor: function(){
        var _this = this;
        this.activeActor.destroy({
            success: function(){
                _this.actorView.close();
                _this.activeActor = null;
                _this.datatable.row('.selected').remove().draw( false );
            },
            error: _this.onError
        });
    }

});
return ActorsView;
}
);
