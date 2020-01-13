
console.log("__LIGHTEDGE_WEBUI",__LIGHTEDGE_WEBUI)

$(document).ready(function() {

  ENTITY = __LIGHTEDGE_WEBUI.ENTITY.MATCHMAP

  // MODAL_FIELD__ADDRESS= "address"
  // MODAL_FIELD__DESCRIPTION= "desc"

  FIELDS = {
    priority: {
      type: "TEXT"
    },
    desc: {
      type: "TEXT"
    },
    ip_proto_num: {
      type: "TEXT"
    },
    dst_ip: {
      type: "TEXT"
    },
    dst_port: {
      type: "TEXT"
    },
    netmask: {
      type: "TEXT"
    },
    new_dst_ip: {
      type: "TEXT"
    },
    new_dst_port: {
      type: "TEXT"
    },
  }

  ADD_MODAL = new WEBUI_Modal_Entity(
    __LIGHTEDGE_WEBUI.MODAL.TYPE.ADD,
    ENTITY
  ).add_fields(FIELDS)

  REMOVE_MODAL = new WEBUI_Modal_Entity(
    __LIGHTEDGE_WEBUI.MODAL.TYPE.REMOVE,
    ENTITY
  ).add_fields(FIELDS)

  aoColumns = [
    { "sTitle": "Priority" },
    { "sTitle": "IP Protocol#" },
    { "sTitle": "DST IP" },
    { "sTitle": "DST Port" },
    { "sTitle": "Netmask" },
    { "sTitle": "NEW DST IP" },
    { "sTitle": "NEW DST Port" },
    { "sTitle": "Actions", "sClass": "text-center" }
  ]

  DATATABLE = $('#dataTable').DataTable({
  "aoColumns": aoColumns
  });

  CF = __LIGHTEDGE_WEBUI.CORE_FUNCTIONS

  refresh_datatable();
});

ENTITY = null
FIELDS = {}
CF = null

function add() {

  let data = {
    "version":"1.0",
    // "addr": ADD_MODAL.address.get(),
    // "desc": ADD_MODAL.desc.get()
  }

  let index = null
  $.each(FIELDS, function(key, val){
    if (key !== 'priority'){
      if ((key === "dst_port") || (key === "new_dst_port") || (key === "ip_proto_num") || (key === "netmask")){
        data[key] = parseInt(ADD_MODAL[key].get())
      }
      else{
        data[key] = ADD_MODAL[key].get()
      }
    }
    else{

      let value = ADD_MODAL[key].get()
      if (CF._is_there(value) && (value !== "")){
        index = value
      }
    }
  })

  if (CF._is_there(index)){
    console.log("priority: ", parseInt(index, 10))  
  }
  else{
    console.log("adding new matchmap with the highest priority") 
  }

  console.log("data: ",data)
  
  add_reset = ADD_MODAL.reset.bind(ADD_MODAL)

  REST_REQ(ENTITY).configure_POST({
    data: data,
    key: index,
    success: [ lightedge_log_response, lightedge_alert_generate_success, 
      add_reset, refresh_datatable ],
    error: [ lightedge_log_response, lightedge_alert_generate_error ]
  })
  .perform()

}

function trigger_remove_modal( matchmap_key ) {

  show_remove_modal = function(data){

    let index = null
    $.each(FIELDS, function(key, val){
      if (key !== 'priority'){
        REMOVE_MODAL[key].set(data[key])
      }
      else{
        REMOVE_MODAL[key].set(matchmap_key)
      }
    })

    // REMOVE_MODAL.address.set(data.addr)
    // REMOVE_MODAL.desc.set(data.desc)

    REMOVE_MODAL.get_$instance().modal({show:true})
  }

  REST_REQ(ENTITY).configure_GET({
    key: matchmap_key,
    success: [ lightedge_log_response, show_remove_modal],
    error: [ lightedge_log_response,  lightedge_alert_generate_error ]
  })
  .perform()
}

function remove(){

  let key = REMOVE_MODAL.priority.get()
  
  REMOVE_MODAL.reset()

  REST_REQ(ENTITY).configure_DELETE({
    key: key,
    success: [
      lightedge_log_response, lightedge_alert_generate_success, refresh_datatable ],
    error: [ lightedge_log_response,  lightedge_alert_generate_error ]
  })
  .perform()
}

function confirm_remove_all(){
  $("#confirm_REMOVE_ALL_Modal").modal({show:true})
}

function remove_all(){
  REST_REQ(ENTITY).configure_DELETE({
    success: [
      lightedge_log_response, lightedge_alert_generate_success, refresh_datatable ],
    error: [ lightedge_log_response,  lightedge_alert_generate_error ]
  })
  .perform()
}


function format_datatable_data( data ) {

  $.each( data, function( key, val ) {

    let index = val['index']+1

    actions = ""+
      // '<button class="btn btn-sm btn-warning shadow-sm mr-xl-1 mb-md-1 m-1" '+
      // 'onclick="trigger_edit_modal(\''+val['addr']+'\')">'+
      // '<i class="fas fa-edit fa-sm fa-fw text-white-50 mr-xl-1 m-1"></i><span class="d-none d-xl-inline">Edit</span></button>'+
      '<button class="btn btn-sm btn-danger shadow-sm mb-xl-1 m-1" '+
      'onclick="trigger_remove_modal(\''+ index +'\')">'+
      '<i class="fas fa-trash fa-sm fa-fw text-white-50 mr-xl-1 m-1"></i><span class="d-none d-xl-inline">Remove</span></button>'

    DATATABLE.row.add([
      "<div class='text-center'>"+index+"</div>",
      val['ip_proto_num'],
      val['dst_ip'],
      val['dst_port'],
      val['netmask'],
      val['new_dst_ip'],
      val['new_dst_port'],
      actions
    ] )

  });

  DATATABLE.draw(true)

}

function refresh_datatable() {

  DATATABLE.clear();
  // if(__LIGHTEDGE_WEBUI.TEST){
  //   REST_REQ(ENTITY).configure_GET({
  //     success: [ format_datatable_data ],
  //     error: [ format_datatable_data ]
  //   })
  //   .perform()
  //   return
  // }
  REST_REQ(ENTITY).configure_GET({
    success: [ lightedge_log_response, format_datatable_data],
    error: [ lightedge_log_response,  lightedge_alert_generate_error ]
  })
  .perform()

  
}