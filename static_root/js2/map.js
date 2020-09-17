/*
    EVERYTHING MAP RELATED
*/

const getLayerFromId = (id) => {
  let layer;
  featureLayer.eachLayer(function (layerCheck) {
    if (parseInt(layerCheck.feature.id) == parseInt(id)) {
      layer = layerCheck;
    }
  });
  return layer;
};

const dataurl = "mapData";
let prevLayersClicked = [];
let prevLayerHovered = null;
let featureLayer;
let mainMap;
let mql = window.matchMedia("(max-width: 768px)");
let zoom = mql.matches ? 6.4 : 6.9;

function changeMapColors() {
  // changes color of icons, when something is clicked. selected values get class 'select' and all the others get class 'base'
  const changeMapColorsPromise = new Promise((resolve, reject) => {
    let selectedStations = $("#id_estacao").val();

    prevLayersClicked = JSON.parse(sessionStorage.getItem("prevLayersClicked"));
    if (prevLayersClicked != null) {
      for (let stationID of prevLayersClicked) {
        if (!selectedStations.includes(stationID)) {
          let layerDeselect = getLayerFromId(stationID);
          layerDeselect.setIcon(createIcon("base"));
        }
      }
    }
    for (let stationID of selectedStations) {
      let layerSelect = getLayerFromId(stationID);
      layerSelect.setIcon(createIcon("select"));
    }

    resolve(selectedStations);
  }).then((selectedStations) => {
    sessionStorage.setItem("prevLayersClicked", JSON.stringify(selectedStations));
  });
}

function createIcon(type) {
  const icon = L.divIcon({
    className: `${type}-icon`,
  });
  return icon;
}

/* Initialize basic map */

mainMap = L.map("mainMap", {
  zoomSnap: 0.1,
  minZoom: 6.6,
}).setView([39.6, -7.8536599], zoom);

L.tileLayer(
  `https://api.mapbox.com/styles/v1/fmacedo/ckav8wl1b49vp1insfxcaywrn/tiles/256/{z}/{x}/{y}@2x?access_token=${mapboxAccessToken}`,
  {
    maxZoom: 18,
    tileSize: 512,
    zoomOffset: -1,
    accessToken: mapboxAccessToken,
  }
).addTo(mainMap);

/* Create searchcontrols */
var GeoSearchControl = window.GeoSearch.GeoSearchControl;
// var OpenStreetMapProvider = window.GeoSearch.OpenStreetMapProvider;
// var provider = new OpenStreetMapProvider({ params: { countrycodes: "PT" } });
var GoogleProvider = window.GeoSearch.GoogleProvider;
var provider = new GoogleProvider({
  params: { key: GmapsApiKey, language: "pt", region: "pt" },
});
//  Define search controls
var searchControl = new GeoSearchControl({
  provider: provider,
  style: "button",
  showMarker: false,
  // marker: {
  // draggable: true,
  // },
  autoComplete: true,
  autoCompleteDelay: 0,
  autoClose: true,
  keepResult: true,
  searchLabel: "Procurar local", // optional: string      - default 'Enter address'
});

// Add searchbar to the map
mainMap.addControl(searchControl);

var info = L.control();

info.onAdd = function (mainMap) {
  this._div = L.DomUtil.create("div", "info"); // create a div with a class "info"
  this.update();
  return this._div;
};

// method that we will use to update the control based on feature properties passed
info.update = function (props) {
  this._div.innerHTML = props
    ? `<p>${props.codigo}</p><p>${props.nome}</p><p>altitude: ${props.altitude} m</p>`
    : "<p>Selecione uma estação</p>";
};

info.addTo(mainMap);

function resetHighlight(e) {
  !e.target._icon.className.split(" ").includes("select-icon") && e.target.setIcon(createIcon("base"));
  // new L.Draw.Rectangle(mainMap, drawControl.options.rectangle).enable();
}
function handleHoverIcon(e) {
  // new L.Draw.Rectangle(mainMap, drawControl.options.rectangle).disable();
  const layer = e.target;

  info.update(layer.feature.properties);
  !layer._icon.className.split(" ").includes("select-icon") && layer.setIcon(createIcon("hover"));
}

function handleClickIcon(e) {
  // new L.Draw.Rectangle(mainMap, drawControl.options.rectangle).disable();
  $(".leaflet-geosearch-button ").removeClass("active");

  const layer = e.target;
  const layerID = layer.feature.id;
  info.update(layer.feature.properties);

  if (event.ctrlKey) {
    selectedVals = $("#id_estacao").select2("val");
    selectedValsUpdated = $("#id_estacao").select2("val").concat(layerID.toString());
  } else {
    selectedValsUpdated = [layerID.toString()];
  }
  $("#id_estacao").val(selectedValsUpdated);
  $("#id_estacao").trigger("change");
  // $("#id_estacao").val(layerID).trigger("change.select2");
  // }
  // if (prevLayerClicked !== layer && prevLayerClicked !== null && !event.ctrlKey) {
  //   // Reset style
  //   prevLayerClicked.setIcon(createIcon("base"));
  // }
}

function onEachFeature(feature, layer) {
  layer.setIcon(createIcon("base"));
  layer.on({
    mouseover: handleHoverIcon,
    mouseout: resetHighlight,
    click: handleClickIcon,
  });
}

// $.getJSON(dataurl, function (data) {
//   L.geoJson(data).addTo(mainMap);
// });

$.getJSON(dataurl, function (data) {
  featureLayer = L.geoJson(data, { onEachFeature: onEachFeature, drawControl: true }).addTo(mainMap);
  $(".select2-selection__choice__remove").changeElementType("span");
  hideMapLoaders();
});
const drawControl = new L.Control.Draw({
  draw: {
    marker: false,
    polygon: false,
    polyline: false,
    rectangle: true,
    circle: false,
    circlemarker: false,
  },
  edit: false,
});

L.drawLocal.draw.toolbar.buttons.rectangle = "Selecionar várias estações";
L.drawLocal.draw.handlers.rectangle.tooltip.start = "Clique e arraste para selecionar várias estações";
L.drawLocal.draw.handlers.simpleshape.tooltip.end = "Liberte o rato para terminar a seleccão";

mainMap.addControl(drawControl);
// new L.Draw.Rectangle(mainMap, drawControl.options.rectangle).enable();

L.Rectangle.include({
  contains: function (latLng) {
    return this.getBounds().contains(latLng);
  },
});

mainMap.on("zoomend", function () {
  zoom = mainMap.getZoom();
  newSize = zoom * 0.1;
  newMargin = -newSize / 2;
  document.documentElement.style.setProperty("--icon-sm", `${newSize}rem`);
  document.documentElement.style.setProperty("--icon-lg", `${newSize * 2}rem`);
  document.documentElement.style.setProperty("--mg-sm", `${newMargin}rem`);
  document.documentElement.style.setProperty("--mg-lg", `${newMargin * 2}rem`);
});

mainMap.on(L.Draw.Event.CREATED, function (e) {
  selectedMarkers = [];
  featureLayer.eachLayer(function (marker) {
    if (e.layer.contains(marker.getLatLng())) {
      selectedMarkers.push(marker.feature.id.toString());
    }
  });

  $("#id_estacao").val(selectedMarkers);
  $("#id_estacao").trigger("change");
  // new L.Draw.Rectangle(mainMap, drawControl.options.rectangle).enable();
});
