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
  $('.ticket-detail-field').filter(":not(.immutable)").hide()
  $('#editTicket').hide()
  $('#saveTicket').show()
  $('#cancelEditTicket').show()
}

function changeToTextFields(){
  $('.input-field').hide()
  $('.ticket-detail-field').filter(":not(.immutable)").show()
  $('#saveTicket').hide()
  $('#cancelEditTicket').hide()
  $('#editTicket').show()
}


function saveEdit(){
  $('#task-form').submit()
}
