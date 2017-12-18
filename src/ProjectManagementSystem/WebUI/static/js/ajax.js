/*********
Creates and sends an AJAX PUT request to update a specific user and profile.
**********/
function updateProduct(){
  $.ajax({
    type: 'PUT',
    url: 'profile_index/',
    data : {
      names : $('#updatedName').val(),
      description : $('#updatedDescription').val(),
      price : $('#updatedPrice').val()
    },
    success: handlingFunctionForUpdating,
    dataType: 'json'
    })
    return false;
}
