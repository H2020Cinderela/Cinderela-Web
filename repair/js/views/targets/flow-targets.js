define(['underscore','views/common/baseview', 'collections/gdsecollection',
        'models/gdsemodel'],

function(_, BaseView, GDSECollection, GDSEModel){
    /**
    *
    * @author Christoph Franke
    * @name module:views/FlowTargetsView
    * @augments Backbone.View
    */
    var FlowTargetsView = BaseView.extend(
        /** @lends module:views/FlowTargetsView.prototype */
        {

        /**
        * render workshop view on flow targets
        *
        * @param {Object} options
        * @param {HTMLElement} options.el                      element the view will be rendered in
        * @param {string} options.template                     id of the script element containing the underscore template to render this view
        * @param {module:models/CaseStudy} options.caseStudy   the casestudy of the keyflow
        * @param {module:models/CaseStudy} options.keyflowId   id of the keyflow to add targets to
        *
        * @constructs
        * @see http://backbonejs.org/#View
        */
        initialize: function(options){
            FlowTargetsView.__super__.initialize.apply(this, [options]);
            var _this = this;
            _.bindAll(this, 'renderObjective');

            this.template = options.template;
            this.caseStudy = options.caseStudy;
            this.keyflowId = options.keyflowId;
            this.keyflowName = options.keyflowName;
            this.aims = options.aims;
            this.userObjectives = options.userObjectives;
            this.targets = {};
            var promises = [];

            this.loader.activate();

            this.userObjectives.forEach(function(objective){
                var targets = new GDSECollection([], {
                    apiTag: 'flowTargets',
                    apiIds: [_this.caseStudy.id, objective.id]
                })
                _this.targets[objective.id] = targets;
                promises.push(targets.fetch({error: _this.onError}));
            })

            this.targetValues = new GDSECollection([], {
                apiTag: 'targetvalues',
            });

            // store last set indicator values here
            this.indValMem = {};

            this.indicators = new GDSECollection([], {
                apiTag: 'flowIndicators',
                apiIds: [this.caseStudy.id, this.keyflowId],
                comparator: 'name'
            });

            promises.push(this.targetValues.fetch({error: _this.onError}))
            promises.push(this.indicators.fetch({error: _this.onError}))

            Promise.all(promises).then(function(){
                _this.loader.deactivate();
                _this.indicators.sort();
                _this.render();
            })
        },

        /*
        * dom events (managed by jquery)
        */
        events: {
        },

        /*
        * render the view
        */
        render: function(){
            var _this = this,
                html = document.getElementById(this.template).innerHTML,
                template = _.template(html);
            this.el.innerHTML = template({
                keyflowName: this.keyflowName
            });
            this.objectivesPanel = document.createElement('div');
            this.el.querySelector('.targets').appendChild(this.objectivesPanel);
            this.userObjectives.forEach(function(objective){
                var panel = _this.renderObjective(objective);
                _this.objectivesPanel.appendChild(panel)
            });
            if (!this.rankingIsValid()) return;
            //this.userObjectives.on("sort", _this.reOrder)
        },

        renderObjective: function(objective){
            var _this = this,
                objectivePanel = document.createElement('div'),
                html = document.getElementById('flow-targets-detail-template').innerHTML,
                template = _.template(html),
                aim = this.aims.get(objective.get('aim')),
                targets = this.targets[objective.id];

            objectivePanel.classList.add('objective-panel');
            objectivePanel.dataset['id'] = objective.id;

            objectivePanel.innerHTML = template({
                id: objective.id,
                title: aim.get('text')
            });

            objectivePanel.querySelector('.overlay').innerHTML = '#' + objective.get('priority');

            var addBtn = objectivePanel.querySelector('button.add'),
                table = objectivePanel.querySelector('.target-table');

            if (targets.length === 0)
                table.style.visibility = 'hidden';

            targets.forEach(function(target){
                _this.renderTargetRow(table, target, objective);
            })

            addBtn.addEventListener('click', function(){
                // create a default Target
                var values = {
                    "indicator": _this.indicators.first().id,
                    "target_value": _this.targetValues.first().id,
                };
                var tVal = _this.indValMem[_this.indicators.first().id];
                // another indicator had a value selected, set it equally
                if (tVal != null) {
                    values['target_value'] = tVal;
                }

                var target = _this.targets[objective.id].create(
                    values,
                    {
                        wait: true,
                        success: function(){
                            table.style.visibility = 'visible';
                            _this.renderTargetRow(table, target, objective);
                        },
                        error: _this.onError
                    }
                );
            })
            return objectivePanel;
        },

        renderTargetRow: function(table, target, objective){
            var _this = this,
                row = table.insertRow(-1),
                indicatorSelect = document.createElement('select'),
                spatialInput = document.createElement('input'),
                targetSelect = document.createElement('select'),
                removeBtn = document.createElement('button');

            indicatorSelect.classList.add('form-control');
            indicatorSelect.classList.add('indicator');
            targetSelect.classList.add('form-control');
            targetSelect.classList.add('target-value');
            row.classList.add('target-row');
            row.dataset['objective'] = objective.id;
            row.dataset['target'] = target.id;
            targetSelect.classList.add('target-value');
            spatialInput.classList.add('form-control');
            spatialInput.disabled = true;

            removeBtn.classList.add("btn", "btn-warning", "square", "remove");
            // removeBtn.style.float = 'right';
            var span = document.createElement('span');
            removeBtn.title = gettext('Remove target')
            span.classList.add('glyphicon', 'glyphicon-minus');
            span.style.pointerEvents = 'none';
            removeBtn.appendChild(span);

            removeBtn.addEventListener('click', function(){
                target.destroy({ success: function(){
                    table.deleteRow(row.rowIndex);
                    if (_this.targets[objective.id].length === 0)
                        table.style.visibility = 'hidden';
                }})
            })

            this.indicators.forEach(function(indicator){
                var option = document.createElement('option');
                option.value = indicator.id;
                option.innerHTML = indicator.get('name');
                indicatorSelect.appendChild(option);
            });
            indicatorSelect.value = target.get('indicator');

            this.targetValues.forEach(function(value){
                var option = document.createElement('option');
                option.value = value.id;
                option.innerHTML = value.get('text');
                targetSelect.appendChild(option);
            });
            targetSelect.value = target.get('target_value');
            this.indValMem[target.get('indicator')] = target.get('target_value')

            function setSpatialRef(indicatorId){
                var spatialRef = _this.indicators.get(indicatorId).get('spatial_reference'),
                    label = (spatialRef === 'REGION') ? gettext('Casestudy Region') : gettext('Focus Area');
                spatialInput.value = label;
            }
            setSpatialRef(target.get('indicator'));

            indicatorSelect.addEventListener('change', function(){
                var tVal = _this.indValMem[this.value],
                    values = { indicator: this.value };
                // another indicator had a value selected, set it equally
                if (tVal != null) {
                    values['target_value'] = tVal;
                    targetSelect.value = tVal;
                }
                target.save(
                    values,
                    { patch: true, error: _this.onError }
                );
                setSpatialRef(this.value);
            })

            targetSelect.addEventListener('change', function(){
                var targetValue = this.value,
                    indicator = indicatorSelect.value,
                    targetRows = _this.el.querySelectorAll('.target-row'),
                    rowArray = Array.prototype.slice.call(targetRows);
                // check all target rows for rows with same indicator
                rowArray.forEach(function(r){
                    var ind = r.querySelector('.indicator').value;
                    if (ind != indicator) return;
                    var tSel = r.querySelector('.target-value'),
                        id = r.dataset['target'],
                        t = _this.targets[r.dataset['objective']].get(id);
                    tSel.classList.add('flash');
                    setTimeout(function() {
                        tSel.classList.remove('flash');
                    }, 500);
                    tSel.value = targetValue;
                    t.save(
                        { target_value: targetValue },
                        { patch: true, error: _this.onError }
                    )
                })
                _this.indValMem[target.get('indicator')] = targetValue;
            })

            row.insertCell(-1).appendChild(indicatorSelect);
            row.insertCell(-1).appendChild(spatialInput);
            row.insertCell(-1).appendChild(targetSelect);
            row.insertCell(-1).appendChild(removeBtn);

        },

        rankingIsValid: function(){
            var valid = true;
            this.userObjectives.forEach(function(objective){
                var priority = objective.get('priority');
                if (priority < 0){
                    valid = false;
                    return;
                }
            })
            var warning = this.el.querySelector('.warning'),
                content = this.el.querySelector('.targets');
            if (this.indicators.length === 0) {
                valid = false;
                warning.innerHTML = gettext('No indicators available for the target definition. Please contact your workshop leader.');
            }
            if (valid) {
                warning.style.display = 'none';
                content.style.display = 'block';
            }
            else {
                warning.style.display = 'block';
                content.style.display = 'none';
            }
            return valid;
        },

        updateOrder(){
            var _this = this;
            // not ready yet (doesn't matter, order comes right after creation)
            if (!this.objectivesPanel || !this.rankingIsValid()) return;
            var objIds = this.userObjectives.pluck('id'),
                first = this.objectivesPanel.firstChild;
            objIds.reverse().forEach(function(id){
                var panel = _this.objectivesPanel.querySelector('.objective-panel[data-id="' + id + '"]');
                panel.querySelector('.overlay').innerHTML = '#' + _this.userObjectives.get(id).get('priority');
                _this.objectivesPanel.insertBefore(panel, first);
                first = panel;
            });
        }

    });
    return FlowTargetsView;
}
);

