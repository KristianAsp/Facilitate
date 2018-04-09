var updating = false;


function updateStateOfTask(taskID, stateID){
    updating = true
    $.ajax({
      type: 'PUT',
      url: '/api/tickets/' + taskID + '/',
      data: {
        'state' : stateID,
      },
      success: function(){
        updating = false;
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
    $("#" + ticket.state).append($("#" + ticket.id))
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
    },
    dataType: 'json',
  })
  return false;
}

/*********
Creates and sends an AJAX PUT request to update a specific user and profile.
**********/
function updateUser(){
  var valid = validateFields()
  if(valid == false){
    return;
  }
  $.ajax({
    type: 'PUT',
    url: '/api/users/',
    data : {
      first_name : $('#first_name').val(),
      last_name : $('#last_name').val(),
      password : $('#password').val(),
      confirm_password : $('#confirm_password').val(),
      current_password : $('#current_password').val(),
      email : $('#email').val(),
      'csrfmiddlewaretoken' : $("input[name=csrfmiddlewaretoken]").val(),
    },
    success: handlingFunctionForUpdating,
    error: handlingFunctionForFailureUpdate,
    dataType: 'json'
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
