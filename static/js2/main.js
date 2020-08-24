/*
    MAIN HANDELING OF EVENTS, WHEN DOCUMENT READY
*/
let flag = false;
document.addEventListener("DOMContentLoaded", function () {
  $(".preloader-background").fadeOut("slow");
  $(".preloader-wrapper").fadeOut();
});

$(document).ready(function () {
  $("#modal1").modal({
    onCloseEnd: function () {
      highlight("startDatepicker");
      highlight("endDatepicker");
    },
  });

  $("#id_estacao").select2({
    placeholder: "Seleccione uma ou mais estações",
    theme: "material",
  });

  $("#id_parametro").select2({
    placeholder: "Seleccione um ou mais parametros",
    theme: "material",
  });
  // .on("select2:open", function () {
  //   $(".select2-results__options").niceScroll();
  // });

  $(".select2-search--inline").append('<span class="material-icons dd-arrow">arrow_drop_down</span>');

  // $("#id_parametro").select2({
  //   placeholder: "Seleccione um ou mais parametros",
  //   theme: "bootstrap",
  //   width: "resolve",
  // });

  $("#id_estacao").on("change", function (e) {
    setSelectionStyle();

    changeMapColors();
  });

  $("#id_parametro").on("change", function (e) {
    setSelectionStyle();
  });

  $("#submitForm").click(function (e) {
    e.preventDefault();
    $("#initial-info").hide();
    let result = checkToMuchData();
    result && handleFormSubmit();
  });
  $(".reset").click(() => {
    $(".leaflet-geosearch-button ").removeClass("active");
  });

  $(".leaflet-draw-draw-rectangle").click(() => {
    $(".leaflet-geosearch-button ").removeClass("active");
  });

  $(".leaflet-control-zoom-out").click(() => {
    $(".leaflet-geosearch-button ").removeClass("active");
  });

  $(".leaflet-control-zoom-in").click(() => {
    $(".leaflet-geosearch-button ").removeClass("active");
  });

  $("#continue-fecth").click(function () {
    handleFormSubmit();
  });
});

$(document).click(function () {
  $(".leaflet-geosearch-button ").removeClass("active");
});
