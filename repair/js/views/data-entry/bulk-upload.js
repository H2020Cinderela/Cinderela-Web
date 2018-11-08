
define(['views/common/baseview', 'underscore', 'models/gdsemodel'],
function(BaseView, _, GDSEModel){

/**
    *
    * @author Christoph Franke
    * @name module:views/BulkUploadView
    * @augments module:views/BaseView
    */
var BulkUploadView = BaseView.extend(
    /** @lends module:views/BulkUploadView.prototype */
    {

    /**
    * render view for bulk uploading keyflow data
    *
    * @constructs
    * @see http://backbonejs.org/#View
    */
    initialize: function(options){
        BulkUploadView.__super__.initialize.apply(this, [options]);
        this.render();
        this.caseStudy = options.caseStudy;
    },

    /*
    * dom events (managed by jquery)
    */
    events: {
        "click button.upload": "upload"
    },

    render: function(){
        BulkUploadView.__super__.render.call(this);
        this.logArea = this.el.querySelector('#upload-log');
    },

    log: function(text){
        this.logArea.innerHTML += '<br>' + text;
        this.logArea.scrollTop = this.logArea.scrollHeight;
    },

    upload: function(evt){
        var _this = this,
            btn = evt.target,
            tag = btn.dataset['tag'];

        var row = this.el.querySelector('.row[data-tag="' + tag +  '"]'),
            input = row.querySelector('input[type="file"]'),
            files = input.files;

        if (files.length === 0){
            this.alert(gettext('No file selected to upload!'));
            return;
        }

        var data = {
            'bulk_upload': files[0]
        }

        var model = new GDSEModel( {}, {
            apiTag: tag, apiIds: [ this.caseStudy.id, this.model.id ]
        });
        this.loader.activate();
        this.log(gettext('Uploading') + ' ' + files[0].name);
        this.log('-----------------------------------------------');
        model.save(data, {
            success: function (res) {
                var res = res.toJSON();
                res.results.forEach(function(m){
                    //if (m.url) delete m.url;
                    _this.log(JSON.stringify(m));
                })
                _this.log('<p style="color: green;">' + gettext('Success') + ': ' + res.added + ' entries added, ' + res.updated + ' entries updated</p>')
                _this.loader.deactivate()
            },
            error: function (res, r) {
                var msg = res.responseJSON.message;
                _this.log('<p style="color: red;">' + gettext('Error') + ': ' + msg + '</p>')
                _this.loader.deactivate()
            },
        });

    }


});
return BulkUploadView;
}
);
