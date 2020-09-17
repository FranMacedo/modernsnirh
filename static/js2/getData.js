/*
    FUNCTIONS TO GET DATA FROM BACKEND
*/

async function handleFormSubmit() {
  flag = false;
  const controller = new AbortController();
  const signal = controller.signal;
  $("#cancel").click(function (e) {
    e.preventDefault();

    flag = true;
    hideLoaders("fast");
    controller.abort();
    console.log(flag);
  });
  // removing all charts, because state manager is hard to setup
  $("#chartsContainer").children("div").remove();
  $("#chartsContainer").children("hr").remove();

  // get selected stations and parameters ids
  let stations = $("#id_estacao").select2("data");
  stations_ids = stations.map((s) => s.id);
  let parameters = $("#id_parametro").select2("data");
  parameters_ids = parameters.map((p) => p.id);

  // check if any of the forms are empty and if so do not proceed
  // if (!checkIfEmpty(stations_ids, parameters_ids)) return;

  // show spinner and setup progress bar values

  $(".preloader-background").hasClass("initial-load") && $(".preloader-background").removeClass("initial-load");
  !$(".preloader-background").hasClass("mid-load") && $(".preloader-background").addClass("mid-load");
  $(".preloader-background").fadeIn("fast");
  $(".preloader-wrapper").fadeIn("fast");

  // $(".overlay").removeClass("no-display");
  let totalProg = stations.length * parameters.length;
  let prog = -1;
  // console.log("initial totalProg", totalProg);
  if (flag) {
    return;
  }
  for (let statID of stations_ids) {
    //loop through selected stations
    for (let paramID of parameters_ids) {
      //loop through selected parameters

      if (flag) {
        return;
      }
      prog += 1;

      //show progress bar and set values (text)
      $("#progressBarContainer").removeClass("no-display");

      $("#progressBar").css("width", `${Math.max((prog / totalProg) * 100, 5)}%`);
      let statName = stations.filter((s) => s.id == statID)[0].text;
      let paramName = parameters.filter((p) => p.id == paramID)[0].text;
      $("#progressBarText").html(
        `<h5 class="center-align">A angariar dados de <b>${paramName}</b> para <b>${statName}</b></h5>`
      );

      // data to pass to the backend
      data = {
        start_date: $("#startDatepicker").val(),
        end_date: $("#endDatepicker").val(),
        stat_id: statID,
        param_id: paramID,
        csrfmiddlewaretoken: csrftoken,
      };

      // fetch data from backend
      let response = await fetch("/", {
        signal,
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

      // await and get data from response and update charts
      let chartsData = await response.json();
      updateCharts(chartsData, statID, paramID, prog, totalProg);

      // $(".preloader-background").fadeOut("fast");
      // $(".preloader-wrapper").fadeOut("fast");
    }
  }
}

function getRedeStations() {
  showMapLoaders();
  let redes = $("#id_rede").select2("data");
  redes_ids = redes.map((r) => r.id);
  data = {
    csrfmiddlewaretoken: csrftoken,
    redes_ids,
  };
  fetch("getStations/", {
    method: "POST",
    credentials: "include",
    body: JSON.stringify(data),
    cache: "no-cache",
    headers: new Headers({
      "X-CSRFToken": csrftoken,

      "content-type": "application/json",
    }),
  })
    .then(function (response) {
      if (response.status !== 200) {
        console.log(`Looks like there was a problem. Status code: ${response.status}`);
        return;
      }
      response.json().then(function (data) {
        mainMap.removeLayer(featureLayer);

        if (data["result"]) {
          featureLayer = L.geoJson(JSON.parse(data["data_map"]), {
            onEachFeature: onEachFeature,
            drawControl: true,
          }).addTo(mainMap);
          setStationsOptions(data["estacoes_select"]);
          setParametersOptions(data["parametros_select"]);
        } else {
          setStationsOptions([]);
          setParametersOptions([]);
        }
        hideMapLoaders();
      });
    })
    .catch(function (error) {
      console.log("Fetch error: " + error);
    });
}

function getStationParameters() {
  let estacoes = $("#id_estacao").select2("data");
  estacoes_ids = estacoes.map((e) => e.id);
  data = {
    csrfmiddlewaretoken: csrftoken,
    estacoes_ids,
  };
  fetch("getParameters/", {
    method: "POST",
    credentials: "include",
    body: JSON.stringify(data),
    cache: "no-cache",
    headers: new Headers({
      "X-CSRFToken": csrftoken,

      "content-type": "application/json",
    }),
  })
    .then(function (response) {
      if (response.status !== 200) {
        console.log(`Looks like there was a problem. Status code: ${response.status}`);
        return;
      }
      response.json().then(function (data) {
        if (data["result"]) {
          setParametersOptions(data["parametros_select"]);
          console.log(data["data_fim"]);
          setDateBeginAndDateEnd(data["data_inicio"], data["data_fim"]);
        } else {
          setParametersOptions([]);
        }
      });
    })
    .catch(function (error) {
      console.log("Fetch error: " + error);
    });
}

function getDatesIntervals() {
  let parametros = $("#id_parametro").select2("data");
  let estacoes = $("#id_estacao").select2("data");

  if (typeof parametros == "undefined" || parametros.length == 0) {
    return;
  }
  console.log("gathering dates intervals..");
  parametros_ids = parametros.map((p) => p.id);
  estacoes_ids = estacoes.map((e) => e.id);

  data = {
    csrfmiddlewaretoken: csrftoken,
    parametros_ids,
  };
  fetch("getDates/", {
    method: "POST",
    credentials: "include",
    body: JSON.stringify(data),
    cache: "no-cache",
    headers: new Headers({
      "X-CSRFToken": csrftoken,

      "content-type": "application/json",
    }),
  })
    .then(function (response) {
      if (response.status !== 200) {
        console.log(`Looks like there was a problem. Status code: ${response.status}`);
        return;
      }
      response.json().then(function (data) {
        if (data["result"]) {
          setDateBeginAndDateEnd(data["data_inicio"], data["data_fim"]);
        }
      });
    })
    .catch(function (error) {
      console.log("Fetch error: " + error);
    });
}
