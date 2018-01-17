define([
  'openlayers', 'ol-contextmenu'
], function(ol, ContextMenu)
{
  /**
   *
   * OpenLayers Map with draggable markers, optional context-menu and fullscreen controls
   *
   * @param {Object} options
   * @param {string} options.divid                        id of the HTMLElement to render the map into
   * @param {string} [options.projection='EPSG:3857']     projection of the map
   * @param {Array.<number>} [options.center=[13.4, 52.5]]  the map will be centered on this point (x, y), defaults to Berlin
   *
   * @author Christoph Franke
   * @name module:visualizations/Map
   * @constructor
   */
  var Map = function(options){
    var idCounter = 0;
    var interactions = [];
    var mapProjection = options.projection || 'EPSG:3857';
    var center = options.center || ol.proj.transform([13.4, 52.5], 'EPSG:4326', mapProjection);

    var view = new ol.View({
      projection: mapProjection,
      center: center,
      zoom: 10
    });
    var vectorLayer = new ol.layer.Vector({ source: new ol.source.Vector() });
  
    var map = new ol.Map({
      layers: [
        new ol.layer.Tile({
          source: new ol.source.OSM({crossOrigin: 'anonymous'}),
        }),
        vectorLayer
      ],
      target: options.divid,
      controls: ol.control.defaults({
        attributionOptions: /** @type {olx.control.AttributionOptions} */ ({
          collapsible: false
        })
      }).extend([
        new ol.control.FullScreen({source: options.divid})
      ]),
      view: view
    });    
    
    /**
     * transforms given coordinates into projection of map
     *
     * @param {Array.<number>} coordinates  (x,y) coordinates to transform
     * @param {string} projection         projection of the coordinate
     *
     * @returns {Array.<number>} (x,y)      coordinates in map projection
     *
     * @method toMapProjection
     * @memberof module:visualizations/Map
     * @instance
     */
    this.toMapProjection = function(coordinate, projection) {
      return ol.proj.transform(coordinate, projection, mapProjection);
    }
    
    /**
     * transforms given coordinates in map projection into given projection
     *
     * @param {Array.<number>} coordinates  (x,y) coordinates in map projection to transform
     * @param {string} projection         projection to transform into
     *
     * @returns {Array.<number>} (x,y)      coordinates in given projection
     *
     * @method toProjection
     * @memberof module:visualizations/Map
     * @instance
     */
    this.toProjection = function(coordinate, projection) {
      return ol.proj.transform(coordinate, mapProjection, projection);
    }
    
    
    /**
     * callback for dragging markers
     *
     * @callback module:visualizations/Map~onDrag
     * @param {Array.<number>} coordinates  (x, y) coordinates in original projection
     */
    
    /**
     * add a marker to map at given position
     *
     * @param {Array.<number>} coordinates    (x,y) coordinates where marker will be added at
     * @param {Object} options
     * @param {string=} options.projection  projection the given coordinates are in, uses map projection if not given
     * @param {string=} [options.name='']   the name will be rendered below the marker
     * @param {string=} options.icon        url to image the marker will be rendered with
     * @param {string=} options.dragIcon    url to image the marker will be rendered with while dragging
     * @param {module:visualizations/Map~onDrag=} options.onDrag      callback that will be called when the marker is dragged to new position
     *
     * @method addmarker
     * @memberof module:visualizations/Map
     * @instance
     */
    this.addmarker = function(coordinates, options) {
      var proj = options.projection || mapProjection;
      
      var template = '({x}, {y})';
          
      var feature = new ol.Feature({
            type: 'removable',
            // transform to map projection
            geometry: new ol.geom.Point(
              this.toMapProjection(coordinates, proj))
          });
      if (options.icon){
         var iconStyle = new ol.style.Style({
          image: new ol.style.Icon({ scale: .08, src: options.icon }),
          text: new ol.style.Text({
            offsetY: 25,
            text: options.name, //ol.coordinate.format(coordinate, template, 2),
            font: '15px Open Sans,sans-serif',
            fill: new ol.style.Fill({ color: '#111' }),
            stroke: new ol.style.Stroke({ color: '#eee', width: 2 })
          })
        });
        feature.setStyle(iconStyle); 
      }
      var dragStyle;
      if (options.dragIcon){
         dragStyle = new ol.style.Style({
          image: new ol.style.Icon({ scale: .08, src: options.dragIcon })
        })
      }
      
      // Drag and drop feature
      var dragInteraction = new ol.interaction.Modify({
          features: new ol.Collection([feature]),
          style: dragStyle,
          pixelTolerance: 20
      });
      
      // Add the event to the drag and drop feature
      dragInteraction.on('modifyend', function(){
        var coordinate = feature.getGeometry().getCoordinates();
        var transformed = ol.proj.transform(coordinate, mapProjection, proj);
        //iconStyle.getText().setText(ol.coordinate.format(transformed, template, 2));
        vectorLayer.changed();
        if(options.onDrag){
          options.onDrag(transformed);
        }        
      }, feature);
      
      interactions.push(dragInteraction);
      map.addInteraction(dragInteraction);
      var id = idCounter;
      feature.setId(id);
      // remember the interactions to access them on remove by setting them as attributes
      feature.onRemove = options.onRemove;
      feature.interaction = dragInteraction;
      idCounter++;
      vectorLayer.getSource().addFeature(feature);
      return id;
    }
    
    /*
    * move marker with given id to given coordinates, not tested yet
    */
    this.moveMarker = function(markerId, coordinates, options) {
      var feature = vectorLayer.getSource().getFeatureById(markerId);
      var options = options || {};
      var proj = options.projection || mapProjection;
      feature.setGeometry(new ol.geom.Point(this.toMapProjection(coordinates, proj)));
    }
    
    /**
     * remove all markers from map
     *
     * @method removeMarkers
     * @memberof module:visualizations/Map
     * @instance
     */
    this.removeMarkers = function(){
      map.getInteractions().forEach(function (interaction) {
          if (interaction instanceof ol.interaction.Modify) 
             map.removeInteraction(interaction);
      });
      vectorLayer.getSource().clear();
    };
    
    // remove marker of given feature
    function removeMarker(obj) {
      var feature = obj.data.marker;
      if (feature.interaction != null) map.removeInteraction(feature.interaction);
      if (feature.onRemove != null) feature.onRemove();
      
      vectorLayer.getSource().removeFeature(feature);
    }
    
    /**
     * callback for clicking item in context menu
     *
     * @callback module:visualizations/Map~itemClicked
     * @param {Object} event event
     * @param {Array.<number>} event.coordinate coordinates in map projection
     * @see https://github.com/jonataswalker/ol-contextmenu
     */
    
    /**
     * add a context menu to the map 
     * option to remove marker and zoom controls are always added
     *
     * @param {Array.<{text: string, icon: string, callback: module:visualizations/Map~itemClicked}>} contextmenuItems  items to be added to the context menu
     *
     * @method addContextMenu
     * @memberof module:visualizations/Map
     * @instance
     * @see https://github.com/jonataswalker/ol-contextmenu
     */
    this.addContextMenu = function (contextmenuItems){
      if (this.contextmenu != null)
        this.map.removeControl(this.contextmenu);
      var contextmenu = new ContextMenu({
        width: 180,
        items: contextmenuItems
      });
      this.contextmenu = contextmenu;
      map.addControl(contextmenu);
      
      var removeMarkerItem = {
        text: 'Remove this Marker',
        classname: 'marker',
        callback: removeMarker
      };
      
      contextmenu.on('open', function (evt) {
        console.log(evt.pixel)
        var feature = map.forEachFeatureAtPixel(evt.pixel, ft => ft);
        
        if (feature && feature.get('type') === 'removable') {
          contextmenu.clear();
          removeMarkerItem.data = { marker: feature };
          contextmenu.push(removeMarkerItem);
        } else {
          contextmenu.clear();
          contextmenu.extend(contextmenuItems);
          contextmenu.extend(contextmenu.getDefaultItems());
        }
      });
    }
    
    map.on('pointermove', function (e) {
      if (e.dragging) return;
    
      var pixel = map.getEventPixel(e.originalEvent);
      var hit = map.hasFeatureAtPixel(pixel);
    
      map.getTargetElement().style.cursor = hit ? 'pointer' : '';
    });
  
    /**
     * center map on given coordinates
     * 
     * @param {Array.<number>} coordinates  (x,y) coordinates 
     * @param {Object} options
     * @param {string=} options.projection  projection of the coordinates, defaults to map projection
     */
    this.center = function(coordinate, options) {
      if (options.projection)
        coordinate = this.toMapProjection(coordinate, options.projection)
      
      view.animate({center: coordinate});//, {zoom: 10});
    }
    
    this.map = map;

  };
  
  
  return Map;
});