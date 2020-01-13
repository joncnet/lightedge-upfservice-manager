$(document).ready(function() {
  refresh_maps();
});

function refresh_maps() {

  update_uemaps = function(data){
    $("#uemap").text(Object.keys(data).length)
  }

  update_matchmaps = function(data){
    $("#matchmap").text(data.length)
  }

  REST_REQ( __LIGHTEDGE_WEBUI.ENTITY.UEMAP).configure_GET({
    success: [ lightedge_log_response, update_uemaps],
    error: [ lightedge_log_response,  lightedge_alert_generate_error ]
  })
  .perform()

  REST_REQ( __LIGHTEDGE_WEBUI.ENTITY.MATCHMAP).configure_GET({
    success: [ lightedge_log_response, update_matchmaps],
    error: [ lightedge_log_response,  lightedge_alert_generate_error ]
  })
  .perform()
}
