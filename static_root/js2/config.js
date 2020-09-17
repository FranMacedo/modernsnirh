const diaSemana = ["Domingo", "Segunda-Feira", "Terca-Feira", "Quarta-Feira", "Quinta-Feira", "Sexta-Feira", "Sabado"];
const meses = [
  "Janeiro",
  "Fevereiro",
  "Marco",
  "Abril",
  "Maio",
  "Junho",
  "Julho",
  "Agosto",
  "Setembro",
  "Outubro",
  "Novembro",
  "Dezembro",
];

const i18n = {
  months: meses,
  monthsShort: ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"],
  weekdays: diaSemana,
  weekdaysShort: ["Dom", "Seg", "Ter", "Qua", "Qui", "Sex", "Sab"],
  weekdaysAbbrev: ["D", "S", "T", "Q", "Q", "S", "S"],
  today: "Hoje",
  clear: "Limpar",
  // cancel: "Sair",
  // done: "Confirmar",
  labelMonthNext: "Próximo mês",
  labelMonthPrev: "Mês anterior",
  labelMonthSelect: "Selecione um mês",
  labelYearSelect: "Selecione um ano",
  selectMonths: true,
  // selectYears: 15,
};

let dateFormat = "dd/mm/yyyy";
const currYear = new Date().getFullYear();

function getDateFromString(dt) {
  let d = parseInt(dt.split("/")[0]);
  let m = parseInt(dt.split("/")[1]) - 1;
  let y = parseInt(dt.split("/")[2]);
  return new Date(y, m, d);
}

$(document).ready(function () {
  $("#startDatepicker-icon").on("click", function (event) {
    event.stopPropagation();
    var element = document.querySelector("#startDatepicker");
    M.Datepicker.getInstance(element).open();
  });
  $("#endDatepicker-icon").on("click", function (event) {
    event.stopPropagation();
    var element = document.querySelector("#endDatepicker");
    M.Datepicker.getInstance(element).open();
  });

  $(".datepicker").datepicker({
    // defaultDate: new Date(currYear - 5, 1, 31),
    // setDefaultDate: new Date(2000,01,31),
    i18n: i18n,
    autoClose: true,
    maxDate: new Date(),
    yearRange: [1850, currYear],
    format: "dd/mm/yyyy",
  });

  function getStringFromDate(dt) {
    return `${dt.getDate()}/${dt.getMonth() + 1}/${dt.getFullYear()}`;
  }
  $("#startDatepicker").change(function () {
    let dateBeginTxt = $("#startDatepicker").val();
    let dateEndTxt = $("#endDatepicker").val();

    let dateBegin = getDateFromString(dateBeginTxt);
    var endElement = document.querySelector("#endDatepicker");

    M.Datepicker.getInstance(endElement).options.minDate = dateBegin;
    console.log(parseInt(dateBeginTxt.split("/")[2]));
    console.log(currYear);
    M.Datepicker.getInstance(endElement).options.yearRange = [parseInt(dateBeginTxt.split("/")[2]), currYear];
    if (dateEndTxt != "") {
      let dateEnd = getDateFromString(dateEndTxt);
      if (dateBegin > dateEnd) {
        console.log("aqui!");

        M.Datepicker.getInstance(endElement).setDate(dateBegin, true);
        $("#endDatepicker").val(dateBeginTxt);
      }
    }
  });
});

function setDateBeginAndDateEnd(dateStartTxt, dateEndTxt) {
  var endElement = document.querySelector("#endDatepicker");
  var startElement = document.querySelector("#startDatepicker");
  dateStart = getDateFromString(dateStartTxt);
  dateEnd = getDateFromString(dateEndTxt);

  M.Datepicker.getInstance(endElement).setDate(dateEnd, true);
  M.Datepicker.getInstance(startElement).setDate(dateStart, true);

  $("#startDatepicker").val(dateStartTxt);
  $("#endDatepicker").val(dateEndTxt);
}
