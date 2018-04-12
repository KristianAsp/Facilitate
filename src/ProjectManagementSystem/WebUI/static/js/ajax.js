


function updateStateOfTask(taskID, stateID){
  var assignee = $('#assigned_to').val()
  var comment = $('#id_new_comment').val()
  $.ajax({
    type: 'PUT',
    url: '/project/tickets/detail/' + taskID + '/',
    data: {
      'state' : stateID,
      'assigned_to' : assignee,
      'comment' : comment,
    },
    success: function(){

    },
    dataType: 'json',
  })
  return false;
}

function concurrencyUpdateBoard(){
  if(shouldUpdateConcurrently == true){
    $.ajax({
      type: 'GET',
      url: '/project/tickets/changes',
      data: {
        'last_modified' : lastUpdatedTime.toLocaleString(),
      },
      success: updatePotentialConcurrentChanges,
      dataType: 'json',
    })
    return false;
  }
}

function updatePotentialConcurrentChanges(){
  var a = this.success.arguments[0].data
  for (var i = 0; i < a.length; i++) {
    ticket = a[i]
    var nameElement = $("#" + ticket.id + " #assigned_to_ticket")
    if($("#" + ticket.state)){
      $("#" + ticket.id + " #assigned_to_ticket").text(ticket.assigned_to);
      $("#" + ticket.state).append($("#" + ticket.id))
    }
    else{
      $("#" + ticket.id).remove()
    }
  }
  lastUpdatedTime = new Date()
}

function fetchUsersForProject(){
  $.ajax({
    type: 'GET',
    url: '/project/settings/users',
    data: {},
    success: function(data){
      availableTags = data;
      $("#assigned_to").autocomplete({
          source: availableTags,
      });
    },
    dataType: 'json',
  })
  return false;
}

function handlingFunctionForUpdating(){
  $('#label').empty()
  $('#label').append('<div class="alert alert-success"><strong>Success!</strong> Your profile has been updated.</div>')
}

function handlingFunctionForFailure(){
  $('#label').empty()
  $('#label').append('<div class="alert alert-danger"><strong>Failure!</strong> Something went wrong. Please try again! If the problem persists, please contact customer support.</div>')
}

function saveTicketEdit(slug, newName){
  var hm =
  $.ajax({
    type: 'PUT',
    url: '/project/tickets/detail/' + slug + '/',
    data : {
      'name' : $('#ticket-name').val(),
    },
    success: handlingFunctionForUpdating,
    dataType: 'json'
    })
    return false;
}
