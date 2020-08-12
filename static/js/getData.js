const sleep = (milliseconds) => {
  return new Promise((resolve) => setTimeout(resolve, milliseconds));
};

let flag = false;
function showSelectAlert(msg) {
  // append alert message to alertContainer
  $("#alertContainer").empty();
  $("#alertContainer").append(`<div class='alert alert-danger'>${msg}</div>`);

  setTimeout(function () {
    $("#alertContainer").children(`div[name=${msg}]`).remove();
  }, 2000);
}

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
      $("#spinner").addClass("no-display");
    });
  }
}

async function handleFormSubmit() {
  // get state
  let state = Object.assign(JSON.parse(sessionStorage.getItem("state")));

  // check if empty selections and show alert
  if (jQuery.isEmptyObject(state["selectedParameters"])) {
    showSelectAlert("É necessário selecionar pelo menos um parâmetro!");
    return;
  } else {
    $("#alertContainer").empty();
  }
  if (jQuery.isEmptyObject(state["selectedStations"])) {
    showSelectAlert("É necessário selecionar pelo menos uma estação!");
    return;
  } else {
    $("#alertContainer").empty();
  }

  //set progress
  let prog = 1;
  totalProg = Object.keys(state["selectedStations"]).length * Object.keys(state["selectedParameters"]).length;
  $("#progressBarContainer").removeClass("no-display");
  $("#spinner").removeClass("no-display");
  $("#progressBar").css("width", `${Math.min((1 / totalProg) * 100 * 0.8, 5)}%`);
  if (flag) {
    return;
  }
  for (let station of Object.keys(state["selectedStations"])) {
    //loop through selected stations
    for (let parameter of Object.keys(state["selectedParameters"])) {
      //loop through selected parameters
      console.log(flag);
      if (flag) {
        $("#progressBarContainer").addClass("no-display");
        $("#spinner").addClass("no-display");
        $("#cancelBarContainer").addClass("no-display");
        return;
      }
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
          updateCharts(chartsData, station, parameter, prog, totalProg);
        } catch (err) {
          console.log("An error occurred while fetching this story.");
        }
        prog += 1;
      } else {
        console.log(`${station} of ${parameter} already exists... next!`);
        console.log("prog", prog);
        console.log("totalProg", totalProg);
        prog += 1;
        if (prog >= totalProg) {
          console.log("yes sir!");
          $("#progressBar").css("width", `100%`);
          sleep(1000).then(() => {
            $("#progressBarContainer").addClass("no-display");
            $("#spinner").addClass("no-display");
          });
        }
      }
    }
  }
}

$("#submitForm").click(function (e) {
  e.preventDefault();
  handleFormSubmit();
});

$("#cancelBtn").click(() => {
  $("#progressBarContainer").addClass("no-display");
  $("#cancelBarContainer").removeClass("no-display");
  flag = true;
});
