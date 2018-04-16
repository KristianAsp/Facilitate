function displayStateButtons(){
    $(".editBtn-State").toggle();
    $(".deleteBtn-State").toggle();
    $(".editState-row").toggle();
}

function applyFiltersOnTasks(){
  var resultSet = $('.ticketTable tr'); //Obtain all tickets.;

  var filters = $('.filter');

  filters.each(function(){
    var filtersToBeApplied = []
    var filterID = this.id
    $('#' + filterID + ' option').each(function(){
      if (this.selected == true){
        filtersToBeApplied.push(this.innerText)
      }
    })
    var filter = ":has("
    for(var i = 0; i < filtersToBeApplied.length; i++){
      if(i > 0){
        filter += ","
      }
      filter += 'td[data-'+filterID+'=\"' + filtersToBeApplied[i] +'\"]'
    }
    filter += ')'
    if(filter != ":has()"){
      resultSet = resultSet.filter(filter)
    }
  })
  showAndHideResult(resultSet)
}

function showAndHideResult(resultSet){
  var fullSet = $('.ticketTable tr').filter(":has(td)"); //Obtain all tickets.;
  fullSet.each(function(){
    $(this).hide()
  })

  resultSet.each(function(){
    $(this).show()
  })
}

function updateNumberOfTasksInStates(){
  var states = $('.individual-state-column')

  states.each(function(){
    var tickets = $(this).find('.unique-ticket')
    var count = tickets.length
    $(this).find('.count')[0].innerText = "(" + count + ")"
  })

}

function changeToInputFields(){
  $('.input-field').show()
  $('.ticket-detail-field, .board-detail-field').filter(":not(.immutable)").hide()
  $('#editTicket, #editBoard').hide()
  $('#saveTicket, #saveBoard').show()
  $('#cancelEditTicket, #cancelEditBoard').show()
}

function changeToTextFields(){
  $('.input-field').hide()
  $('.ticket-detail-field, .board-detail-field').filter(":not(.immutable)").show()
  $('#saveTicket, #saveBoard').hide()
  $('#cancelEditTicket, #cancelEditBoard').hide()
  $('#editTicket, #editBoard').show()
}


function saveEdit(){
  $('#edit-form').submit()
}

function updateOrderOfStates(){
  var statesInOrder = $('.state').filter(":not(.gu-mirror)")
  var data = ""
  var labels = [];
  statesInOrder.each(function(){
    labels.push($(this).data('id'))
  })
  data = labels.join(', ')
  sendUpdateToDB(data)
}

function openNewStateModal(){
  $('#newStateModal').modal('show')
}

function addNewStateRow(){
  var name = $('#state_name').val()
  var short_name = $('#state_short_name').val()
  $('#newStateModal').modal('hide')

  addNewState(name, short_name)
  updateOrderOfStates()
}


function changeSettingTab(button){
  var attribute = $(button).data('attribute')
  var element = $(".board-settings[data-tab=" + attribute + "]").removeClass('hidden-setting').addClass('display-setting')
  var elements = $(".board-settings:not([data-tab=" + attribute + "])").removeClass('display-setting').addClass('hidden-setting')

  $('.nav-tabs li').removeClass('active')
  $(button.parentNode).addClass('active')
}
