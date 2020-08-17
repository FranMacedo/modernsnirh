/*
    MAIN HANDELING OF EVENTS, WHEN DOCUMENT READY
*/
let flag = false;
document.addEventListener("DOMContentLoaded", function () {
  $(".preloader-background").fadeOut("slow");
  $(".preloader-wrapper").fadeOut();
});

$(document).ready(function () {
  $(".datepicker").datepicker({
    startDate: "-3d",
  });
  // $("#id_estacao").select2({
  //   placeholder: "Seleccione uma ou mais estações",
  //   theme: "bootstrap",
  //   width: "resolve",
  // });

  $("#id_estacao").select2({
    placeholder: "Seleccione uma ou mais estações",
    theme: "material",
  });

  $("#id_parametro").select2({
    placeholder: "Seleccione um ou mais parametros",
    theme: "material",
  });

  $(".select2-search--inline").append('<span class="material-icons dd-arrow">arrow_drop_down</span>');
  $("select")
    .select2()
    .on("select2:open", function () {
      $(".select2-results__options").niceScroll();
    });
  // $("#id_parametro").select2({
  //   placeholder: "Seleccione um ou mais parametros",
  //   theme: "bootstrap",
  //   width: "resolve",
  // });

  $("#id_estacao").on("change", function (e) {
    $(".select2-selection__choice__remove").length && $(".select2-selection__choice__remove").changeElementType("span");
    changeMapColors();
  });

  $("#id_parametro").on("change", function (e) {
    $(".select2-selection__choice__remove").length && $(".select2-selection__choice__remove").changeElementType("span");
  });

  $("#submitForm").click(function (e) {
    e.preventDefault();
    $("#initial-info").hide();
    handleFormSubmit();
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

  $("#cancelBtn").click(() => {
    $("#progressBarContainer").addClass("no-display");
    $("#cancelBarContainer").removeClass("no-display");
    flag = true;
  });
});

$(document).click(function () {
  $(".leaflet-geosearch-button ").removeClass("active");
});
