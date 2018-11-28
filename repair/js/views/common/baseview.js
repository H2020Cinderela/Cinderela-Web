define(['backbone', 'underscore', 'utils/utils', 'app-config',
    'hierarchy-select', 'hierarchy-select/dist/hierarchy-select.min.css'],
function(Backbone, _, utils, config){
/**
*
* @author Christoph Franke
* @name module:views/BaseView
* @augments Backbone.View
*/
var BaseView = Backbone.View.extend(
    /** @lends module:views/BaseView.prototype */
    {

    /**
    * Basic View with common functions, may be extended by other views
    *
    * @param {Object} options
    * @param {HTMLElement} options.el                   element the view will be rendered in (Backbone.View parameter)
    * @param {string} options.template                  id of the script element containing the underscore template to render this view
    * @param {Backbone.Model=} options.model            (Backbone.View parameter)
    * @param {Backbone.Collection=} options.collection  (Backbone.View parameter)
    *
    * @constructs
    * @see http://backbonejs.org/#View
    */
    initialize: function(options){
        _.bindAll(this, 'render');
        _.bindAll(this, 'alert');
        _.bindAll(this, 'onError');
        var _this = this;
        this.template = options.template;
        this.loader = new utils.Loader(options.el, {disable: true});
        this.projection = 'EPSG:4326';
    },

    /**
    * DOM events (jQuery style)
    */
    events: {
    },

    /**
    * render the view with template into element
    */
    render: function(){
        var html = document.getElementById(this.template).innerHTML,
            template = _.template(html);
        this.el.innerHTML = template();
    },

    /** format a number to currently set language **/
    format: function(value){
        return value.toLocaleString(this.language);
    },

    /**
    * callback for selecting items in the hierarchical select
    *
    * @callback module:views/BaseView~onSelect
    * @param {Backbone.Model} model  the selected model
    */

    /**
    * build a hierarchical selection of a collection, the collection has to be
    * of tree structure where the parents of a child are referenced by an attribute (options.parentAttr)
    * absence of parent indicates a root item
    *
    * @param {Backbone.Collection} collection       models of collection will be the items of the hierarchical select
    * @param {HTMLElement}                          the element to append the rendered hierarchical select to
    * @param {String} [options.parentAttr='parent'] the name of attribute referencing the id of the parent model
    * @param {module:views/BaseView~onSelect=} options.onSelect  function is called on selection of an item
    * @param {Number=} options.selected             preselects the model with given id
    * @param {Number} [options.selected=400]        preselects the model with given id
    */
    hierarchicalSelect: function(collection, parent, options){

        var wrapper = document.createElement("div"),
            options = options || {},
            width = options.width || 400,
            parentAttr = options.parentAttr || 'parent',
            defaultOption = options.defaultOption || 'All',
            items = [];

        // make a list out of the collection that is understandable by treeify and hierarchySelect
        collection.each(function(model){
            var item = {};
            var name = model.get('name');
            item.text = name.substring(0, 70);
            if (name.length > 70) item.text += '...';
            item.title = model.get('name');
            item.level = 1;
            item.id = model.id;
            item.parent = model.get(parentAttr);
            item.value = model.id;
            items.push(item);
        })

        var treeList = utils.treeify(items);

        // converts tree to list sorted by appearance in tree,
        // stores the level inside the tree as an attribute in each node
        function treeToLevelList(root, level){
            var children = root['nodes'] || [];
            children = children.slice();
            delete root['nodes'];
            root.level = level;
            list = [root];
            children.forEach(function(child){
                list = list.concat(treeToLevelList(child, level + 1));
            })
            return list;
        };

        var levelList = [];
        treeList.forEach(function(root){ levelList = levelList.concat(treeToLevelList(root, 1)) });

        // load template and initialize the hierarchySelect plugin
        var inner = document.getElementById('hierarchical-select-template').innerHTML,
            template = _.template(inner),
            html = template({ options: levelList, defaultOption: defaultOption });
        wrapper.innerHTML = html;
        wrapper.name = 'material';
        parent.appendChild(wrapper);
        var select = wrapper.querySelector('.hierarchy-select');
        $(select).hierarchySelect({
            width: width
        });

        // preselect an item
        if (options.selected){
            var selection = select.querySelector('.selected-label');
            var model = collection.get(options.selected);
            if (model){
                // unselect the default value
                var li = select.querySelector('li[data-default-selected]');
                li.classList.remove('active');
                selection.innerHTML = model.get('name');
                var li = select.querySelector('li[data-value="' + options.selected + '"]');
                if (li) li.classList.add('active');
            }
        }

        // event click on item
        var anchors = select.querySelectorAll('a');
        for (var i = 0; i < anchors.length; i++) {
            anchors[i].addEventListener('click', function(){
                var item = this.parentElement;
                var model = collection.get(item.getAttribute('data-value'));
                wrapper.title = item.title;
                if (options.onSelect) options.onSelect(model);
            })
        }
        return select;
    },

    /**
    * show a modal with given alert message
    *
    * @param {String} message           html formatted message to show
    * @param {String} [title='Warning'] title displayed in header of modal
    */
    alert: function(message, title){
        var title = title || gettext('Warning');
        var el = document.getElementById('alert-modal'),
            html = document.getElementById('alert-modal-template').innerHTML,
            template = _.template(html);

        el.innerHTML = template({ title: title, message: message });
        $(el).modal('show');
    },

    /**
    * create a bootstrap alert (dismissible div)
    *
    * @param {String} message                      the message displayed inside the alert
    * @param {Object=} options
    * @param {Object=} options.parentEl            alert will be added to this div
    * @param {String=} options.type                type of the alert ('success', 'danger', 'warning', 'info')
    * @param {Boolean} [options.dismissible=false] alert is dismissible (cross for closing alert)
    */
    bootstrapAlert: function(message, options){
        var options = options || {},
            type = options.type || 'success'
            alertDiv = document.createElement('div');

        alertDiv.classList.add('alert', 'alert-' + type, 'fade', 'in')
        alertDiv.innerHTML = message;

        if (options.dismissible){
            alertDiv.classList.add('alert-dismissible');
            var a = document.createElement('a');
            a.setAttribute('href', '#');
            a.classList.add('close');
            a.dataset['dismiss'] = 'alert';
            a.innerHTML = 'x';
            alertDiv.appendChild(a);
        }

        if (options.parentEl)
            options.parentEl.appendChild(alertDiv);
        return alertDiv;
    },

    /**
    * show a modal with given info message
    *
    * @param {String} message           html formatted message to show
    * @param {String} [title='Warning'] title displayed in header of modal
    */
    info: function(message, options){
        var options = options || {},
            title = options.title || gettext('Info');
        var el = options.el || document.getElementById('info-modal'),
            html = document.getElementById('info-modal-template').innerHTML,
            template = _.template(html);

        el.innerHTML = template({ title: title, message: message });
        $(el).modal('show');
    },


    /**
    * show a modal with error message on server error
    * you may pass the model and response or response only
    *
    * @param {Object} arg1        model or AJAX response
    * @param {Object=} arg2       AJAX response (if arg1 is model)
    */
    onError: function(arg1, arg2){
        var response = (arg1.status) ? arg1 : arg2;
        message = response.statusText + '<br><br>';
        if (response.responseText)
            message += '<b>' + gettext('The server responded with: ') + '</b><br>' + '<i>' + response.responseText + '</i>';
        this.alert(message, gettext('Error <b>' + response.status + '</b>'));
    },


    /**
    * callback for confirming a confirmation modal
    *
    * @callback module:views/BaseView~onConfirm
    */

    /**
    * callback for confirming user input of name
    *
    * @callback module:views/BaseView~onNameConfirm
    * @param {String} name  the user input
    */

    /**
    * show a modal to enter a name
    *
    * @param {Object=} options
    * @param {module:views/BaseView~onNameConfirm} options.onConfirm  called when user confirms input
    * @param {String} [options.title='Name'] title of the modal
    */
    getName: function(options){

        var options = options || {};

        var el = document.getElementById('generic-modal'),
            inner = document.getElementById('empty-modal-template').innerHTML;
            template = _.template(inner),
            html = template({ header:  options.title || 'Name' });

        el.innerHTML = html;
        var body = el.querySelector('.modal-body');

        var row = document.createElement('div');
        row.classList.add('row');
        var label = document.createElement('div');
        label.innerHTML = gettext('Name');
        var input = document.createElement('input');
        input.style.width = '100%';
        input.value = options.name || '';
        body.appendChild(row);
        row.appendChild(label);
        row.appendChild(input);

        el.querySelector('.confirm').addEventListener('click', function(){
            if (options.onConfirm) options.onConfirm(input.value);
            $(el).modal('hide');
        });

        $(el).modal('show');
    },

    /**
    * show a modal to enter inputs (not tested for anything but text, might have
    * to be extended for number support etc.)
    *
    * @param {Object} options
    * @param {Object=} options.onConfirm  called when user confirms input
    * @param {String} [options.title='Confirm Inputs'] title of the modal
    * @param {Object} options.inputs inputs with names as keys and as values object with keys 'type' (values: 'textarea', 'checkbox', 'text', etc), label (values: String) and value (values: prefilled value)
    */
    getInputs: function(options){

        var el = document.getElementById('generic-modal'),
            inner = document.getElementById('empty-modal-template').innerHTML;
            template = _.template(inner),
            html = template({ header:  options.title || 'Confirm Inputs' });

        el.innerHTML = html;
        var body = el.querySelector('.modal-body'),
            values = options.values || {},
            inputs = {};

        Object.keys(options.inputs).forEach(function(key){
            var obj = options.inputs[key],
                row = document.createElement('div'),
                label = document.createElement('div');
            var input = (obj.type === 'textarea') ? document.createElement('textarea'): document.createElement('input');
            row.classList.add('row');
            label.innerHTML = obj.label || key;
            input.type = obj.type || 'text';
            input.value = obj.value || '';
            input.style.width = '100%';
            input.style.maxWidth = '100%';
            input.style.minWidth = '100%';
            body.appendChild(row);
            row.appendChild(label);
            row.appendChild(input);
            inputs[key] = input
        })

        el.querySelector('.confirm').addEventListener('click', function(){
            if (options.onConfirm) {
                var ret = {};
                Object.keys(inputs).forEach(function(key){
                    ret[key] = inputs[key].value;
                })
                options.onConfirm(ret);
            }
            $(el).modal('hide');
        });

        $(el).modal('show');
    },

    /**
    * show a modal to confirm sth
    *
    * @param {Object=} options
    * @param {module:views/BaseView~onConfirm} options.onConfirm  called when user confirmed dialog
    * @param {String} options.message  message in dialog
    */
    confirm: function(options){
        var options = options || {},
            html = document.getElementById('confirmation-template').innerHTML,
            template = _.template(html),
            elConfirmation = document.getElementById('confirmation-modal'),
            elements = options.elements || [];
        elConfirmation.innerHTML = template({ message: options.message || '' });
        var body = elConfirmation.querySelector('.modal-body');
        elements.forEach(function(el){
            body.appendChild(el);
        })
        var confirmBtn = elConfirmation.querySelector('.confirm'),
            cancelBtn = elConfirmation.querySelector('.cancel');
        if (options.onConfirm)
            confirmBtn.addEventListener('click', options.onConfirm)
        if (options.onCancel)
            cancelBtn.addEventListener('click', options.onCancel)
        $(elConfirmation).modal('show');
    },

    /**
    * unbind the events and remove this view from the DOM and
    */
    close: function(){
        this.undelegateEvents(); // remove click events
        this.unbind(); // Unbind all local event bindings
        this.el.innerHTML = ''; //empty the DOM element
    }

});
return BaseView;
}
);
