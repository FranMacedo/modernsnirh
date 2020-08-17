/*
    FUNCTIONS TO GET DATA FROM BACKEND
*/

async function handleFormSubmit() {
  // removing all charts, because state manager is hard to setup
  $("#chartsContainer").children("div").remove();
  $("#chartsContainer").children("hr").remove();

  // get selected stations and parameters ids
  let stations = $("#id_estacao").select2("data");
  stations_ids = stations.map((s) => s.id);
  let parameters = $("#id_parametro").select2("data");
  parameters_ids = parameters.map((p) => p.id);

  // check if any of the forms are empty and if so do not proceed
  if (!checkIfEmpty(stations_ids, parameters_ids)) return;

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
        // flag tells if user clicked "cancel" button and stop gathering data if so
        hidelLoaders("fast");
        $("#cancelBarContainer").addClass("no-display");
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
        stat_id: statID,
        param_id: paramID,
        csrfmiddlewaretoken: csrftoken,
      };

      // fetch data from backend
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

      // await and get data from response and update charts
      let chartsData = await response.json();
      updateCharts(chartsData, statID, paramID, prog, totalProg);

      // $(".preloader-background").fadeOut("fast");
      // $(".preloader-wrapper").fadeOut("fast");
    }
  }
}
