/*
    GENERAL FUNCTIONS TO USE
*/
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

function sleep(ms) {
  // sleep for some "ms" miliseconds
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function triggerDownload(chart, type) {
  // trigger download of specific chart, with specific type of file (csv, pdf, excel...)

  switch (type) {
    case "excel":
      chart.downloadXLS();
      break;
    case "csv":
      chart.downloadCSV();
      break;
    case "pdf":
      chart.exportChart({
        type: "application/pdf",
      });
      break;
    case "png":
      chart.exportChart({
        type: "image/png",
      });
      break;
    default:
      return;
  }
}

function hidelLoaders(velocity = "fast") {
  // hide both spinner and progressabar

  $("#progressBarContainer").addClass("no-display");

  $(".preloader-background").fadeOut(velocity);
  $(".preloader-wrapper").fadeOut(velocity);
  return true;
}

function showToast(msg, toastClass) {
  var toastHTML = `<span>${msg}</span><button class="btn-flat toast-action" style="color: white">x</button>`;
  M.toast({ html: toastHTML, classes: toastClass });
  $(".toast-action").click(function (e) {
    $(this)
      .parent()
      .fadeOut("fast", function () {
        $(this).parent().remove();
      });
  });
}

function checkIfEmpty(est_ids, param_ids) {
  // check if any of the stations and parameters form is empty, show alert if so and return false. otherwise, return true
  if (jQuery.isEmptyObject(est_ids) && jQuery.isEmptyObject(param_ids)) {
    showToast("É necessário selecionar pelo menos um parâmetro e uma estação!", "danger-toast");
    return false;
  } else if (jQuery.isEmptyObject(param_ids)) {
    showToast("É necessário selecionar pelo menos um parâmetro!", "danger-toast");
    return false;
  } else if (jQuery.isEmptyObject(est_ids)) {
    showToast("É necessário selecionar pelo menos uma estação!", "danger-toast");
    return false;
  } else {
    // $("#alertContainer").empty();
  }
  return true;
}

function setChartHeight(chart) {
  // changes chart height depending of number of series in it, to be more visible
  let newHeight = 400;
  if (chart.series.length > 5) {
    newHeight = 500;
  } else if (chart.series.length > 10) {
    newHeight = 600;
  } else if (chart.series.length > 15) {
    newHeight = 700;
  } else if (chart.series.length > 20) {
    newHeight = 800;
  }

  chart.setSize(chart.chartWidth, newHeight);
}

const setDownloadTrigger = (chartID) => {
  // set download trigger for specific chartID, so it is ready to download when clicked
  $(`.downloadChart[name=${chartID}]`).click(function (e) {
    e.preventDefault();

    let chart = $(`#${$(this).attr("name")}`).highcharts();
    let type = $(this).attr("id");

    triggerDownload(chart, type);
  });
};

async function updateCharts(data, station, parameter, prog, totalProg) {
  // function that creates or updates charts, depending if they exist already, or just shows alerts, if something goes wrong.

  if (data["stat"] === "true") {
    // if we have data, go for it
    let chartID = `chart_${parameter}`;
    let seriesID = `${station}_${parameter}`;

    let chartName = `${data["parameter_name"]}`;
    let seriesName = `${data["station_name"]}`;
    let chartData = JSON.parse(data["data"]);

    if (!$(`#${chartID}`).highcharts()) {
      // if we don't have this chart in the browser, start it up.
      get_chart(chartID, chartName, seriesName, seriesID, data["un"], chartData, data["chartType"]);
      setDownloadTrigger(chartID);
    } else {
      // if we already have this chart in the browser, just add new series to it.
      var chart = $(`#${chartID}`).highcharts();
      chart.addSeries({
        id: seriesID,
        name: seriesName,
        data: chartData,
        type: data["chartType"],
      });

      // change height if to many charts
      setChartHeight(chart);
    }

    // updating chart state, not currently necessary
    // if (typeof $("body").data(chartID) == "undefined") {
    //   $("body").data(chartID, [seriesID]);
    // } else {
    //   $("body").data(chartID).push(seriesID);
    // }
  } else if (data["stat"] == "error") {
    // if there's some kind of unforeseen error, show danger message
    let msg = data["msg"] ? `: ${data["msg"]}` : "";
    showToast(`<b>Erro a reunir os dados pretendidos</b>${msg}`, "danger-toast");
  } else {
    // if there's no data for this chart, show warning message
    showToast(
      `sem dados para a estação <b>${data["station_name"]}</b> para o parametro <b>${data["parameter_name"]}</b>`,
      "warning-toast"
    );
  }

  // set progressbar width
  $("#progressBar").css("width", `${(prog + 1 / totalProg) * 100}%`);
  if (prog == totalProg - 1) {
    // if we have all data loaded, wait for 1 sec and hide everything
    await sleep(1000);
    hidelLoaders("slow");
  }
}

function setSelectionStyle() {
  if ($(".select2-selection__choice__remove").length) {
    $(".select2-selection__choice__remove").changeElementType("span");
    $(".dd-arrow").addClass("no-display");
  } else {
    $(".dd-arrow").removeClass("no-display");
  }
}
