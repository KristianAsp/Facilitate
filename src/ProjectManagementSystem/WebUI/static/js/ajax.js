function updateStateOfTask(taskID, stateID){
  $.ajax({
    type: 'PUT',
    url: '/api/tickets/' + taskID + '/',
    data: {
      'state' : stateID,
    },
    success: {},
    dataType: 'json',
  })
  return false;
}
