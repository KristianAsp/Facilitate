
var x = document.getElementsByClassName("ticket-column");
var availableTags = fetchUsersForProject()

dragula(Array.from(x))
        .on('drop', function (el, target, source) {

          var btn = $("#myInput")

          $('#myModal').on('shown.bs.modal', function(){
            $("#myInput").autocomplete({
              source: availableTags,
            });
          });
          $(".cancelUpdate").click(function(){
            source.appendChild(el);
            return;
          });

          $("#update").click(function(){
            var result = validateUpdate()
            if(result == false){
              return;
            }
            else{
              $('#myModal').modal('hide');
              updateStateOfTask(el.id, target.id)
            }
          });
          if(target.id != "BL"){
            $('#myModal').modal('show');

          }
         });

function lol(id) {
  return document.getElementById(id);
}


function validateUpdate(){
  return true;
}



function updateClubdays(button){

}
