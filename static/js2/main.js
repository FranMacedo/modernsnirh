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
let flag = false;
function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

$(document).ready(function () {
  $(".datepicker").datepicker({
    startDate: "-3d",
  });
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
    changeMapColors();
  });

  $("#id_parametro").on("change", function (e) {
    $(".select2-selection__choice__remove").length && $(".select2-selection__choice__remove").changeElementType("span");
  });

  $("#submitForm").click(function (e) {
    e.preventDefault();
    handleFormSubmit();
  });

  $("#cancelBtn").click(() => {
    $("#progressBarContainer").addClass("no-display");
    $("#cancelBarContainer").removeClass("no-display");
    flag = true;
  });
});

function hidelLoaders() {
  $("#progressBarContainer").addClass("no-display");
  $("#spinner").addClass("no-display");
  return true;
}

function showSelectAlert(msg) {
  // append alert message to alertContainer
  $("#alertContainer").empty();
  $("#alertContainer").append(`<div class='alert alert-danger alert-dismissible fade show'>${msg}
  <button type="button" class="close" data-dismiss="alert" aria-label="Close">
  <span aria-hidden="true">&times;</span>
</button>
  </div>`);
}

function showMissAlert(msg) {
  // append alert message to alertContainer
  $("#alertMissContainer").empty();
  $("#alertMissContainer").append(`<div class='alert alert-warning alert-dismissible fade show'>${msg}
  <button type="button" class="close" data-dismiss="alert" aria-label="Close">
  <span aria-hidden="true">&times;</span>
</button>
  </div>`);
}

function checkIfEmpty(est_ids, param_ids) {
  if (jQuery.isEmptyObject(est_ids) && jQuery.isEmptyObject(param_ids)) {
    showSelectAlert("É necessário selecionar pelo menos um parâmetro e uma estação!");
    return false;
  } else {
    $("#alertContainer").empty();
  }
  if (jQuery.isEmptyObject(param_ids)) {
    showSelectAlert("É necessário selecionar pelo menos um parâmetro!");
    return false;
  } else {
    $("#alertContainer").empty();
  }
  if (jQuery.isEmptyObject(est_ids)) {
    showSelectAlert("É necessário selecionar pelo menos uma estação!");
    return false;
  } else {
    $("#alertContainer").empty();
  }
  return true;
}

async function updateCharts(data, station, parameter, prog, totalProg) {
  if (data["stat"] === "true") {
    let chartID = `chart_${parameter}`;
    let seriesID = `${station}_${parameter}`;

    let chartName = `${data["parameter_name"]}`;
    let seriesName = `${data["station_name"]}`;
    let chartData = JSON.parse(data["data"]);

    if (!$(`#${chartID}`).highcharts()) {
      get_chart(chartID, chartName, seriesName, seriesID, data["un"], chartData, data["chartType"]);
    } else {
      // console.log("chart ja existe! adiciona series...");
      var chart = $(`#${chartID}`).highcharts();
      chart.addSeries({
        id: seriesID,
        name: seriesName,
        data: chartData,
        type: data["chartType"],
      });
    }

    // updating chart state
    if (typeof $("body").data(chartID) == "undefined") {
      $("body").data(chartID, [seriesID]);
    } else {
      $("body").data(chartID).push(seriesID);
    }
  } else {
    showMissAlert(
      `sem dados para a estação <b>${data["station_name"]}</b> para o parametro <b>${data["parameter_name"]}</b>`
    );
    console.log("algum erroo");
  }

  $("#progressBar").css("width", `${(prog + 1 / totalProg) * 100}%`);
  // console.log("prog vai: ", prog);
  if (prog == totalProg - 1) {
    // console.log("o prog ja esta igual  ao totalProg!");
    await sleep(1000);
    hidelLoaders();
  }
}

async function checkIfRemovedSeries(stationsIDS, parametersIDS, isSeries) {
  // console.log("state data before: ", $("body").data());
  // console.log("stationsIDS: ", stationsIDS);
  // console.log("parametersIDS: ", parametersIDS);

  for (let chartID in $("body").data()) {
    let allSeriesIDS = $("body").data(chartID);
    // console.log("checking ALL THIS seriesID: ", allSeriesIDS);

    for (let seriesID of allSeriesIDS) {
      // console.log("checking seriesID: ", seriesID);

      if (!stationsIDS.includes(seriesID.split("_")[0])) {
        // means this series ID has been removed from the dropdown
        // console.log("series has been removed: ", seriesID);

        if (isSeries) {
          let chart = $(`#${chartID}`).highcharts();

          if (typeof chart != "undefined") {
            chart.series.length <= 2 ? $(`#${chartID}`).remove() : chart.get(seriesID).remove();
          }
        } else {
          if (typeof $("body").data(chartID) != "undefined") {
            let index = $("body").data(chartID).indexOf(seriesID);
            if (index > -1) {
              $("body").data(chartID).splice(index, 1);
            }
          }
        }
      }
    }
  }
  // console.log("state data after: ", $("body").data());
}
async function handleFormSubmit() {
  $("#chartsContainer").children("div").remove();
  $("#chartsContainer").children("hr").remove();

  let stations = $("#id_estacao").select2("data");
  stations_ids = stations.map((s) => s.id);
  let parameters = $("#id_parametro").select2("data");
  parameters_ids = parameters.map((p) => p.id);

  if (!checkIfEmpty(stations_ids, parameters_ids)) return;

  // data = {
  //   stations: stations_ids,
  //   parameters: parameters_ids,
  //   csrfmiddlewaretoken: csrftoken,
  // };

  // await checkIfRemovedSeries(stations_ids, parameters_ids, true);
  // await checkIfRemovedSeries(stations_ids, parameters_ids, false);

  $("#spinner").removeClass("no-display");
  let totalProg = stations.length * parameters.length;
  let prog = -1;
  // console.log("initial totalProg", totalProg);
  if (flag) {
    return;
  }
  for (let statID of stations_ids) {
    //loop through selected stations
    for (let paramID of parameters_ids) {
      if (flag) {
        $("#progressBarContainer").addClass("no-display");
        $("#spinner").addClass("no-display");
        $("#cancelBarContainer").addClass("no-display");
        return;
      }
      prog += 1;

      $("#progressBarContainer").removeClass("no-display");
      $("#spinner").removeClass("no-display");

      $("#progressBar").css("width", `${Math.max((prog / totalProg) * 100, 5)}%`);

      let statName = stations.filter((s) => s.id == statID)[0].text;
      let paramName = parameters.filter((p) => p.id == paramID)[0].text;

      $("#progressBarText").html(`A angariar dados de <b>${paramName}</b> para <b>${statName}</b>`);

      data = {
        stat_id: statID,
        param_id: paramID,
        csrfmiddlewaretoken: csrftoken,
      };
      let response = await fetch("/", {
        method: "POST", // *GET, POST, PUT, DELETE, etc.
        mode: "cors", // no-cors, *cors, same-origin
        cache: "no-cache", // *default, no-cache, reload, force-cache, only-if-cached
        credentials: "same-origin", // include, *same-origin, omit
        headers: {
          "X-CSRFToken": csrftoken,
          "Content-Type": "application/json",
          // 'Content-Type': 'application/x-www-form-urlencoded',
        },
        // redirect: "follow", // manual, *follow, error
        // referrerPolicy: "no-referrer", // no-referrer, *no-referrer-when-downgrade, origin, origin-when-cross-origin, same-origin, strict-origin, strict-origin-when-cross-origin, unsafe-url
        body: JSON.stringify(data), // body data type must match "Content-Type" header
      });
      let chartsData = await response.json();
      updateCharts(chartsData, statID, paramID, prog, totalProg);
      $("#spinner").removeClass("no-display");
    }
  }
}
