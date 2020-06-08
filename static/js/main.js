(function ($) {
  $.fn.changeElementType = function (newType) {
    var attrs = {};

    $.each(this[0].attributes, function (idx, attr) {
      attrs[attr.nodeName] = attr.nodeValue;
    });

    this.replaceWith(function () {
      return $("<" + newType + "/>", attrs).append($(this).contents());
    });
  };
})(jQuery);

const getLayerFromId = (id) => {
  let layer;
  featureLayer.eachLayer(function (layerCheck) {
    if (layerCheck.feature.id == id) {
      layer = layerCheck;
    }
  });
  return layer;
};

// const mapboxAccessToken = "pk.eyJ1IjoiZm1hY2VkbyIsImEiOiJjanp0a3FlZzEwNXdyM2hteDRmOTNsZDI3In0.UMzEBHFVDraOT5AkHcbe7A";
const dataurl = "mapData";
let prevLayersClicked = [];
let prevLayerHovered = null;
let featureLayer;

$(document).ready(function () {
  $("#id_estacao").select2({
    placeholder: "Seleccione uma ou mais estações",
    theme: "bootstrap",
  });
  $("#id_parametro").select2({
    placeholder: "Seleccione um ou mais parametros",
    theme: "bootstrap",
  });

  $("#id_estacao").on("change", function (e) {
    $(".select2-selection__choice__remove").length && $(".select2-selection__choice__remove").changeElementType("span");
    // selectedStations = $("#id_estacao").val();
    updateStationState($("#id_estacao").select2("data"));
    let state = JSON.parse(sessionStorage.getItem("state"));

    for (let stationID of prevLayersClicked) {
      if (!Object.keys(state["selectedStations"]).includes(stationID)) {
        const layerDeselect = getLayerFromId(stationID);
        layerDeselect.setIcon(createIcon("base"));
      }
    }

    for (let stationID of Object.keys(state["selectedStations"])) {
      if (prevLayersClicked.includes(stationID)) {
        break;
      }
      featureLayer.eachLayer(function (layerCheck) {
        if (layerCheck.feature.id == parseInt(stationID)) {
          layerCheck.setIcon(createIcon("select"));
          prevLayersClicked.push(layerCheck.feature.id);
        }
      });
    }
  });
  $("#id_parametro").on("change", function (e) {
    $(".select2-selection__choice__remove").length && $(".select2-selection__choice__remove").changeElementType("span");
    // selectedParameters = $("#id_parametro").val();
    updateParameterState($("#id_parametro").select2("data"));
  });
});

function createIcon(type) {
  const icon = L.divIcon({
    className: `${type}-icon`,
  });
  return icon;
}

let mql = window.matchMedia("(max-width: 768px)");
let zoom = mql.matches ? 6.4 : 6.9;

var mainMap = L.map("mainMap", {
  zoomSnap: 0.1,
  minZoom: 6.6,
}).setView([39.6, -7.8536599], zoom);

L.tileLayer(
  "https://api.mapbox.com/styles/v1/fmacedo/ckav8wl1b49vp1insfxcaywrn/tiles/256/{z}/{x}/{y}@2x?access_token=pk.eyJ1IjoiZm1hY2VkbyIsImEiOiJjanp0a3FlZzEwNXdyM2hteDRmOTNsZDI3In0.UMzEBHFVDraOT5AkHcbe7A",
  {
    maxZoom: 18,
    tileSize: 512,
    zoomOffset: -1,
    accessToken: "pk.eyJ1IjoiZm1hY2VkbyIsImEiOiJjanp0a3FlZzEwNXdyM2hteDRmOTNsZDI3In0.UMzEBHFVDraOT5AkHcbe7A",
  }
).addTo(mainMap);

var info = L.control();

info.onAdd = function (mainMap) {
  this._div = L.DomUtil.create("div", "info"); // create a div with a class "info"
  this.update();
  return this._div;
};

// method that we will use to update the control based on feature properties passed
info.update = function (props) {
  this._div.innerHTML = props ? `<h5>${props.nome}</h5>` : "<h5>selecione uma estação</h5>";
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
