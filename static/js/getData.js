const sleep = (milliseconds) => {
  return new Promise((resolve) => setTimeout(resolve, milliseconds));
};

function updateCharts(data, station, parameter, prog, totalProg) {
  if (data["stat"] === "true") {
    let chartID = `chart_${parameter}`;
    let seriesID = `${station}_${parameter}`;

    let chartName = `${data["parameter_name"]}`;
    let seriesName = `${data["station_name"]}`;
    let chartData = JSON.parse(data["data"]);

    if (!$(`#${chartID}`).highcharts()) {
      get_chart(chartID, chartName, seriesName, seriesID, data["un"], chartData);
    } else {
      console.log("chart ja existe! adiciona series...");
      var chart = $(`#${chartID}`).highcharts();
      chart.addSeries({
        id: seriesID,
        name: seriesName,
        data: chartData,
      });
    }
    updateChartState(station, parameter);
  } else {
    console.log("algum erroo");
  }
  $("#progressBar").css("width", `${(prog / totalProg) * 100}%`);
  if (prog == totalProg) {
    sleep(1000).then(() => {
      $("#progressBarContainer").addClass("no-display");
    });
  }
  $("#spinner").addClass("no-display");
}

async function handleFormSubmit() {
  let state = Object.assign(JSON.parse(sessionStorage.getItem("state")));
  let prog = 1;
  totalProg = Object.keys(state["selectedStations"]).length * Object.keys(state["selectedParameters"]).length;
  $("#progressBarContainer").removeClass("no-display");

  $("#progressBar").css("width", `${5}%`);
  for (let station of Object.keys(state["selectedStations"])) {
    for (let parameter of Object.keys(state["selectedParameters"])) {
      if (!(state["stationChart"][station] && state["stationChart"][station].includes(`${parameter}`))) {
        console.log(`start of ${station} of ${parameter}`);
        $("#progressBarText").html(
          `A angariar dados de <b>${state["selectedParameters"][parameter]}</b> para <b>${state["selectedStations"][station]}</b>`
        );
        data = {
          station: station,
          parameter: parameter,
          csrfmiddlewaretoken: csrftoken,
        };
        let getDataUrl = "/";
        try {
          let response = await fetch(getDataUrl, {
            method: "POST", // *GET, POST, PUT, DELETE, etc.
            mode: "cors", // no-cors, *cors, same-origin
            cache: "no-cache", // *default, no-cache, reload, force-cache, only-if-cached
            credentials: "same-origin", // include, *same-origin, omit
            headers: {
              "X-CSRFToken": csrftoken,
              "Content-Type": "application/json",
              // 'Content-Type': 'application/x-www-form-urlencoded',
            },
            redirect: "follow", // manual, *follow, error
            referrerPolicy: "no-referrer", // no-referrer, *no-referrer-when-downgrade, origin, origin-when-cross-origin, same-origin, strict-origin, strict-origin-when-cross-origin, unsafe-url
            body: JSON.stringify(data), // body data type must match "Content-Type" header
          });

          let chartsData = await response.json();
          console.log(chartsData);
          updateCharts(chartsData, station, parameter, prog, totalProg);
        } catch (err) {
          console.log("An error occurred while fetching this story.");
        }
      }
      prog += 1;
    }
  }
}

$("#submitForm").click(function (e) {
  e.preventDefault();
  $("#spinner").removeClass("no-display");
  handleFormSubmit();
});
