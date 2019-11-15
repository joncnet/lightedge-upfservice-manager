
$(document).ready(function() {

  aoColumns = [
          { "sTitle": "Address" },
          { "sTitle": "Description" },
          { "sTitle": "Last seen" },
          { "sTitle": "Address" },
  ]

  t = $('#dataTable').DataTable({
      "aoColumns": aoColumns
  });

  refresh();

});


function refresh() {

}
