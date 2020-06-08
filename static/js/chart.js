function get_chart(chartID, chartName, seriesName, seriesID, un, data) {
  // var node = document.getElementById("myList2").lastChild;
  // document.getElementById("myList1").appendChild(node);
  $("#chartsContainer").append(`<div id=${chartID} ></div>`);
  chart = Highcharts.stockChart(chartID, {
    chart: {
      zoomType: "x",
      //                backgroundColor: 'transparent'
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
        '<td style="padding:0"> <b> {point.y:.1f}  mm</b></td></tr>',
      footerFormat: "</table>",
      xDateFormat: "%d %B %Y",
      shared: true,
      useHTML: true,
    },
    legend: {
      enabled: false,
    },

    title: {
      text: chartName,
    },

    subtitle: {
      text: "Selecione o intervalo de tempo pretendido",
    },
    plotOptions: {
      area: {
        fillColor: {
          linearGradient: {
            x1: 0,
            y1: 0,
            x2: 0,
            y2: 1,
          },
          stops: [
            [0, Highcharts.getOptions().colors[0]],
            [1, Highcharts.color(Highcharts.getOptions().colors[0]).setOpacity(0.3).get("rgba")],
          ],
        },
        marker: {
          radius: 2,
        },
        lineWidth: 1,
        states: {
          hover: {
            lineWidth: 1,
          },
        },
        threshold: null,
      },
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
      },
    ],
  });
  // $("#button").click(function () {
  //   chart.exportChart();
  // });
}
