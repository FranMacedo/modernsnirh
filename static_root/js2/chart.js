function add_btns(containerId, classID) {
  $(containerId).append("<span class='mr-1 align-text-bottom'><small>Download</small></span>");
  $(containerId).append(
    `<a name="${classID}" class='downloadChart' id='excel' href="#" title='download em EXCEL (.xls)'><i class="fa fa-file-excel fa-lg"></i></a>`
  );
  $(containerId).append(
    `<a name="${classID}" class='downloadChart' id='csv'  href="#" title='download em CSV (.csv)'><i class="fa fa-file-csv fa-lg"></i></a>`
  );
  $(containerId).append(
    `<a name="${classID}" class='downloadChart' id='pdf'  href="#" title='download em PDF (.pdf)'><i class="fa fa-file-pdf fa-lg"></i></a>`
  );
  $(containerId).append(
    `<a name="${classID}" class='downloadChart' id='png'  href="#" title='download de IMAGEM (.png)'><i class="fa fa-file-image fa-lg"></i></a>`
  );
}

function get_chart(chartID, chartName, seriesName, seriesID, un, data, chartType = "line") {
  // var node = document.getElementById("myList2").lastChild;
  // document.getElementById("myList1").appendChild(node);
  $("#chartsContainer").append(`<div class="row mt-3"><div id="${chartID}Btns" class="right mr-2"></div></div>`);
  add_btns(`#${chartID}Btns`, chartID);
  $("#chartsContainer").append(`<div id=${chartID} style: "height:400px"></div>`);
  $("#chartsContainer").append("<div class='divider'></div>");
  chart = Highcharts.stockChart(chartID, {
    chart: {
      zoomType: "x",
      backgroundColor: "transparent",
      height: 400,
    },

    rangeSelector: {
      buttons: [
        {
          type: "month",
          count: 6,
          text: "6 meses",
        },
        {
          type: "year",
          count: 1,
          text: "1 ano",
        },
        {
          type: "year",
          count: 5,
          text: "5 anos",
        },
        {
          type: "year",
          count: 10,
          text: "10 anos",
        },
        {
          type: "all",
          text: "Total",
        },
      ],
      buttonTheme: {
        width: 60,
      },
      selected: 2,
    },
    navigator: {
      margin: 10,
      height: 70,
    },

    yAxis: {
      title: {
        text: `<p   style="text-align: center">${chartName}<br><span>${un}</span></p>`,
      },
      opposite: false,
    },
    labels: {
      //                staggerLines: 1,
      formatter: function () {
        return Highcharts.dateFormat("%b %Y", this.value);
      },
    },

    tooltip: {
      headerFormat: '<span style="font-size:10px">{point.key}</span><table>',
      pointFormat:
        '<tr><td style="color:{series.color};padding:0">{series.name}: </td>' +
        `<td style="padding:0"> <b> {point.y:.1f}  ${un}</b></td></tr>`,
      footerFormat: "</table>",
      xDateFormat: "%d %B %Y",
      shared: true,
      useHTML: true,
    },
    legend: {
      enabled: true,
      maxHeight: 70,
    },

    title: {
      text: chartName,
    },

    exporting: {
      buttons: {
        contextButton: {
          enabled: false,
        },
      },

      chartOptions: {
        chart: {
          backgroundColor: "#f4f4f4",
        },
        title: {
          // text: sessionStorage.getItem("chartExportTitle") != undefined ? sessionStorage.getItem("chartExportTitle") : "",
          style: {
            fontSize: 10,
          },
        },
        subtitle: {
          style: {
            fontSize: 8,
          },
        },
        rangeSelector: {
          enabled: false,
          inputEnabled: true,
        },
        navigator: {
          enabled: false,
        },
      },
    },

    subtitle: {
      text: "Selecione o intervalo de tempo pretendido",
    },

    seriesOptions: {
      dataGrouping: {
        approximation: "sum",
      },
    },
    series: [
      {
        id: seriesID,
        name: seriesName,
        data: data,
        type: chartType,
      },
    ],
  });
  // $("#button").click(function () {
  //   chart.exportChart();
  // });
  // $("#chartID").css("overflow", "inherit");
}
