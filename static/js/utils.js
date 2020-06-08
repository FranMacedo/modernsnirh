// let state = {
//   selectedStations: [],
//   selectedParameters: [],
//   stationChart: {},
// };
$(document).ready(function () {
  sessionStorage.setItem(
    "state",
    JSON.stringify({
      selectedStations: {},
      selectedParameters: [],
      stationChart: {},
    })
  );
  console.log("begin!: ", JSON.parse(sessionStorage.getItem("state")));

  console.log($("id_estacao").children());
});

const updateStationState = (stationsAfter) => {
  statIDs = stationsAfter.map((s) => s.id);

  statIDsNames = stationsAfter.reduce((obj, item) => {
    obj[item.id] = item.text;
    return obj;
  }, {});

  let state = Object.assign(JSON.parse(sessionStorage.getItem("state")));
  for (let s of Object.keys(state["selectedStations"])) {
    if (!statIDs.includes(s)) {
      $("#chartsContainer")
        .children("div")
        .each(function () {
          console.log($(this));
          let p = $(this).attr("id").split("_")[1];
          let chart = $(this).highcharts();
          chart.series.length <= 2 ? $(this).remove() : chart.get(`${s}_${p}`).remove();
          let currentStationCharts = state["stationChart"][s];
          if (currentStationCharts) {
            state["stationChart"][s] = currentStationCharts.filter((v) => {
              v != p;
            });
          }
        });
    }
  }

  state["selectedStations"] = statIDsNames;
  // state["statIDsNames"] = statIDsNames;
  // console.log("after: ", state);
  sessionStorage.setItem("state", JSON.stringify(state));
};

const updateParameterState = (paramAfterRaw) => {
  let state = Object.assign(JSON.parse(sessionStorage.getItem("state")));

  paramAfter = paramAfterRaw.reduce((obj, item) => {
    obj[item.id] = item.text;
    return obj;
  }, {});

  for (let p of Object.keys(state["selectedParameters"])) {
    if (!Object.keys(paramAfter).includes(p)) {
      $("#chartsContainer")
        .children("div")
        .each(function () {
          let p_chart = $(this).attr("id").split("_")[1];
          if (p_chart === p) {
            $(this).remove();
            let currentSC = state["stationChart"];
            if (currentSC) {
              for (let s in currentSC) {
                let currentSPC = state["stationChart"][s];
                state["stationChart"][s] = currentSPC.filter((vp) => vp !== p);
              }
            }
          }
        });
    }
  }

  state["selectedParameters"] = paramAfter;

  // console.log("after: ", state);
  sessionStorage.setItem("state", JSON.stringify(state));
};

const updateChartState = (s, p) => {
  let state = Object.assign(JSON.parse(sessionStorage.getItem("state")));
  if (!state["stationChart"][s]) {
    state["stationChart"][s] = [p.toString()];
  } else {
    state["stationChart"][s].push(p.toString());
  }
  sessionStorage.setItem("state", JSON.stringify(state));
  // console.log("after: ", state);
};
