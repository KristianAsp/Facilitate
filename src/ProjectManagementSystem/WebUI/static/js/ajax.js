function updateStateOfTask(taskID, stateID){
  var csrftoken = getCookie('csrftoken');
  setRequestHeader(csrftoken);

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
  var hasUpdated = false;
  for (var i = 0; i < a.length; i++) {
    hasUpdated = true;
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
  if(hasUpdated){
    updateNumberOfTasksInStates()
  }
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
  var csrftoken = getCookie('csrftoken');
  setRequestHeader(csrftoken);

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

function sendUpdateToDB(data){
  var csrftoken = getCookie('csrftoken');
  setRequestHeader(csrftoken);

  $.ajax({
    type: 'POST',
    url: '/project/boards/states/update',
    data: {
      'data' : data,
    },
    success: function(){

    },
    dataType: 'json',
  })
  return false;
}

function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

function setRequestHeader(csrftoken){
    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });
}


function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function addNewState(name, short_name){
  var csrftoken = getCookie('csrftoken');
  setRequestHeader(csrftoken);

  $.ajax({
    type: 'POST',
    url: '/project/boards/states/new',
    data: {
      'name' : name,
      'short_name' : short_name,
    },
    success: handleSuccessWhenAddingState,
    dataType: 'json',
  })
  return false;
}

function copyNewState(name, short_name, pk){
  var csrftoken = getCookie('csrftoken');
  setRequestHeader(csrftoken);

  $.ajax({
    type: 'POST',
    url: '/project/boards/states/copy/' + pk,
    data: {
      'name' : name,
      'short_name' : short_name,
    },
    success: handleSuccessWhenCopyingState,
    dataType: 'json',
  })
  return false;
}

function handleSuccessWhenAddingState(){
    var state = this.success.arguments[0]
    var csrfToken = "<input type='hidden' name='csrfmiddlewaretoken' value='" + getCookie('csrftoken') + "'>"
    var valToAppend = '<div data-id="' + state.state_id + '"class="list-group-item state"><span style="margin-right: 1em;" class="glyphicon glyphicon-th"></span>'+ state.short_name +' - '+ state.name +'<form method="POST" action="/dashboard/delete/' + state.short_name + '/"><button type="submit" style="float:right"> &times;</button>' + csrfToken + ' </form></div>';
    $('#state-list').append(valToAppend)
}

function handleSuccessWhenCopyingState(){
    var state = this.success.arguments[0]
    var csrfToken = "<input type='hidden' name='csrfmiddlewaretoken' value='" + getCookie('csrftoken') + "'>"
    var valToAppend = '<div data-name="' + state.short_name + '"class="list-group-item state"><span style="margin-right: 1em;" class="glyphicon glyphicon-th"></span>'+ state.short_name +' - '+ state.name +'<form method="POST" action="/dashboard/delete/' + state.short_name + '/"><button type="submit" style="float:right"> &times;</button>' + csrfToken + ' </form></div>';
    $('#state-list').append(valToAppend)
    var ele = $('li[data-name='+ state.short_name +']')
    ele.remove()
}
