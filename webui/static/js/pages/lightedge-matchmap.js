
console.log("__LIGHTEDGE_WEBUI",__LIGHTEDGE_WEBUI)

$(document).ready(function() {

  CF = __LIGHTEDGE_WEBUI.CORE_FUNCTIONS

  ENTITY = __LIGHTEDGE_WEBUI.ENTITY.MATCHMAP

  // MODAL_FIELD__ADDRESS= "address"
  // MODAL_FIELD__DESCRIPTION= "desc"

  DEFAULT_PRIORITY_VALUE = 1
  DEFAULT_DESCRIPTION_VALUE = ""
  DEFAULT_IP_PROTOCOL_SELECT_VALUE = 6 // TCP protocol
  DEFAULT_IP_PROTOCOL_NUMBER_VALUE = 6
  DEFAULT_IP_PROTOCOL_NUMBER_CUSTOM_VALUE = 0
  DEFAULT_DESTINATION_IP_VALUE = ""
  DEFAULT_DESTINATION_PORT_VALUE = 0
  DEFAULT_NETMASK_VALUE = 32
  DEFAULT_NEW_DESTINATION_IP_VALUE = ""
  DEFAULT_NEW_DESTINATION_PORT_VALUE = 0

  IP_PROTOCOL_SELECT_OPTIONS = [
    {
      label: "ICMP",
      value: 1,
      allow_port: false
    },
    {
      label: "TCP",
      value: 6,
      allow_port: true
    },
    {
      label: "UDP",
      value: 17,
      allow_port: true
    },
    {
      label: "SCTP",
      value: 132,
      allow_port: true
    },
    {
      label: "CUSTOM",
      value: "",
      allow_port: false
    }
  ]

  FIELDS = {
    priority: {
      type: "TEXT",
      default: DEFAULT_PRIORITY_VALUE,
    },
    desc: {
      type: "TEXT",
      default: DEFAULT_DESCRIPTION_VALUE
    },
    ip_proto_select: {
      type: "SELECT",
      default: DEFAULT_IP_PROTOCOL_SELECT_VALUE,
    },
    ip_proto_num: {
      type: "TEXT",
      default: DEFAULT_IP_PROTOCOL_NUMBER_VALUE
    },
    dst_ip: {
      type: "TEXT",
      default: DEFAULT_DESTINATION_IP_VALUE
    },
    dst_port: {
      type: "TEXT",
      default: DEFAULT_DESTINATION_PORT_VALUE
    },
    netmask: {
      type: "TEXT",
      default: DEFAULT_NETMASK_VALUE
    },
    new_dst_ip: {
      type: "TEXT",
      default: DEFAULT_NEW_DESTINATION_IP_VALUE
    },
    new_dst_port: {
      type: "TEXT",
      default: DEFAULT_NEW_DESTINATION_PORT_VALUE
    },
  }

  ADD_MODAL = new WEBUI_Modal_Entity(
    __LIGHTEDGE_WEBUI.MODAL.TYPE.ADD,
    ENTITY
  ).add_fields(FIELDS)

  reset2modal_defaults(__LIGHTEDGE_WEBUI.MODAL.TYPE.ADD)

  update_description()

  REMOVE_MODAL = new WEBUI_Modal_Entity(
    __LIGHTEDGE_WEBUI.MODAL.TYPE.REMOVE,
    ENTITY
  ).add_fields(FIELDS)

  aoColumns = [
    { "sTitle": "Priority" },
    { "sTitle": "Description" },
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

  refresh_datatable();
});

ENTITY = null
FIELDS = {}
CF = null

function reset_modal_ip_proto_select_options(modal_type){
  let modal = null
  switch(modal_type){
    case __LIGHTEDGE_WEBUI.MODAL.TYPE.ADD:
      modal = ADD_MODAL
      break
    case __LIGHTEDGE_WEBUI.MODAL.TYPE.REMOVE:
      modal = REMOVE_MODAL
      break
  }
  if (CF._is_there(modal)){
    let options = []
    IP_PROTOCOL_SELECT_OPTIONS.forEach(function(option){
      let label = option.label + " ["+option.value+"]"
      if (option.label === "CUSTOM"){
        label = option.label
      }
      options.push({
        label: label,
        value: option.value
      })
    })
    modal.ip_proto_select.reset(options)
  }
}

function reset2modal_defaults(modal_type){
  switch(modal_type){
    case __LIGHTEDGE_WEBUI.MODAL.TYPE.ADD:
      $.each(FIELDS, function(key, data){
        if (key === "ip_proto_select"){
          reset_modal_ip_proto_select_options(modal_type)
          ADD_MODAL[key].set(data.default)
        }
        ADD_MODAL[key].set(data.default)
      })
      break
    case __LIGHTEDGE_WEBUI.MODAL.TYPE.REMOVE_MODAL:
      break
  }
}

function add() {

  let data = {
    "version":"1.0",
    // "addr": ADD_MODAL.address.get(),
    // "desc": ADD_MODAL.desc.get()
  }

  let index = null
  $.each(FIELDS, function(key, val){
    if (key !== 'priority'){
      if (key === "ip_proto_select"){
        // skip this params
      }
      else if ((key === "dst_port") || (key === "new_dst_port") || (key === "ip_proto_num") || (key === "netmask")){
        data[key] = parseInt(ADD_MODAL[key].get())
        if (Number.isNaN(data[key])){
          switch(key){
            case "new_dst_port":
              data[key] = DEFAULT_NEW_DESTINATION_PORT_VALUE
              break
            case "dst_port":
              data[key] = DEFAULT_DESTINATION_PORT_VALUE
              break
            case "ip_proto_num":
              data[key] = DEFAULT_IP_PROTOCOL_NUMBER_CUSTOM_VALUE
              break
            case "netmask":
              data[key] = DEFAULT_NETMASK_VALUE
              break
          }
        }
        console.log(key, data[key])
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
      else{
        index = DEFAULT_PRIORITY_VALUE
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

  // if (true){
  //   show_remove_modal({
  //     priority: matchmap_key,
  //     desc: "Tutto farlocco"
  //   })
  // }
  // else{
    REST_REQ(ENTITY).configure_GET({
      key: matchmap_key,
      success: [ lightedge_log_response, show_remove_modal],
      error: [ lightedge_log_response,  lightedge_alert_generate_error ]
    })
    .perform()
  // }
}

function remove(){

  let key = REMOVE_MODAL.priority.get()

  console.log("matchmap TO BE REMOVED, key: ", key)
  
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
      '<button class="btn btn-sm btn-danger shadow-sm mb-xl-1 m-1" '+
      'onclick="trigger_remove_modal(\''+ index +'\')">'+
      '<i class="fas fa-trash fa-sm fa-fw text-white-50 mr-xl-1 m-1"></i><span class="d-none d-xl-inline">Remove</span></button>'

    DATATABLE.row.add([
      "<div class='text-center'>"+index+"</div>",
      val['desc'],
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

  console.log("refreshing datatable")

  DATATABLE.clear();
  REST_REQ(ENTITY).configure_GET({
    success: [ lightedge_log_response, format_datatable_data],
    error: [ lightedge_log_response,  lightedge_alert_generate_error ]
  })
  .perform()

  
}

function update_description(){
  
  let description = ADD_MODAL["desc"].get()
  // console.log("update_description, value = '"+description+"'")
  let button = $("#add_button")
  if (CF._is_there(description) &&
     (description !== "")){
    // console.log("enabled")
    CF._enable(button)
  }
  else{
    // console.log("disabled")
    CF._disable(button)
  }
}

function update_selected_pn(op){
  let modal = null
  let select_wrapper = null
  let input_wrapper = null
  let dst_port_wrapper = null
  let new_dst_port_wrapper = null
  switch(op){
    case "ADD":
      modal = ADD_MODAL
      select_wrapper = $("#add_ip_proto_select_wrapper")
      input_wrapper = $("#add_ip_proto_num_wrapper")
      dst_port_wrapper = $("#add_dst_port_wrapper")
      new_dst_port_wrapper = $("#add_new_dst_port_wrapper")
      break
  }
  if (CF._is_there(modal)){
    let select = modal.ip_proto_select
    let input = modal.ip_proto_num

    input.set(select.get())

    let value = input.get()

    IP_PROTOCOL_SELECT_OPTIONS.some(function(elem){
      console.log(elem.value, value)
      if ((""+elem.value) === (""+value)){
          // ALLOW PORTS
          enable_ports("ADD", elem.allow_port)
          if (elem.allow_port){
            dst_port_wrapper.removeClass("d-none")
            new_dst_port_wrapper.removeClass("d-none")
          }
          else{
            dst_port_wrapper.addClass("d-none")
            new_dst_port_wrapper.addClass("d-none")   
          }
          // CUSTOM option
          if (value === ""){
            CF._enable(input.$instance)
            select_wrapper.removeClass("col-8 pr-0")
            select_wrapper.addClass("col-4 pr-1")
            input_wrapper.removeClass("d-none")
          }
          else{
            CF._disable(input.$instance)
            select_wrapper.addClass("col-8 pr-0")
            select_wrapper.removeClass("col-4 pr-1")
            input_wrapper.addClass("d-none")
          }
          return true
      }
    })
  }
}

function enable_ports(op, enable){
  let modal = null
  switch(op){
    case "ADD":
      modal = ADD_MODAL
      break
  }
  if (CF._is_there(modal)){
    let port = modal.dst_port
    let new_port = modal.new_dst_port
    if (enable){
      console.log("enabling",op,enable)
      CF._enable(port.$instance)
      CF._enable(new_port.$instance)
    }
    else{
      console.log("disabling",op,enable)
      port.set(DEFAULT_DESTINATION_PORT_VALUE)
      new_port.set(DEFAULT_NEW_DESTINATION_PORT_VALUE)

      CF._disable(port.$instance)
      CF._disable(new_port.$instance)

    }
   

  }
}