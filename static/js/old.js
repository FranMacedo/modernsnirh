async function postData(url = "", data = {}) {
  // Default options are marked with *
  const response = await fetch(url, {
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
  return await response.json(); // parses JSON response into native JavaScript objects
}

function getUpdate(station, parameter, prog, totalProg) {
  $("#spinner").removeClass("no-display");
  let data = {
    station: station,
    parameter: parameter,
    csrfmiddlewaretoken: csrftoken,
  };
  postData("/", data).then((data) => {
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
  });

  // $.ajax({
  //   type: "POST",
  //   url: "/",
  //   async: true,
  //   data: {
  //     station: station,
  //     parameter: parameter,
  //     csrfmiddlewaretoken: csrftoken,
  //   },
  //   cache: false,
  //   success: function (data) {
  //     if (data["stat"] === "true") {
  //       let chartID = `chart_${parameter}`;
  //       let seriesID = `${station}_${parameter}`;

  //       let chartName = `${data["parameter_name"]}`;
  //       let seriesName = `${data["station_name"]}`;
  //       let chartData = JSON.parse(data["data"]);

  //       if (!$(`#${chartID}`).highcharts()) {
  //         get_chart(chartID, chartName, seriesName, seriesID, data["un"], chartData);
  //       } else {
  //         console.log("chart ja existe! adiciona series...");
  //         var chart = $(`#${chartID}`).highcharts();
  //         chart.addSeries({
  //           id: seriesID,
  //           name: seriesName,
  //           data: chartData,
  //         });
  //       }
  //       updateChartState(station, parameter);
  //       console.log(`end of ${station} of ${parameter}`);
  //     } else {
  //       console.log("algum erroo");
  //     }
  //     $("#spinner").addClass("no-display");

  //     // let presentCharts = state["stationChart"];
  //   },
  // });
}

async function handleFormSubmit() {
  let state = Object.assign(JSON.parse(sessionStorage.getItem("state")));
  let prog = 0;
  totalProg = state["selectedStations"].length * state["selectedParameters"].length;
  $("#progressBar").css("width", `${5}%`);

  for (let station of state["selectedStations"]) {
    for (let parameter of state["selectedParameters"]) {
      if (!(state["stationChart"][station] && state["stationChart"][station].includes(`${parameter}`))) {
        console.log(`start of ${station} of ${parameter}`);
        $("#progressBarContainer").removeClass("no-display");
        prog += 1;
        console.log(prog, totalProg);

        try {
          getUpdate(station, parameter, prog, totalProg);
        } catch (e) {
          console.error(e.message);
        }
        console.log(`end of ${station} of ${parameter}`);
      }
    }
  }
}
