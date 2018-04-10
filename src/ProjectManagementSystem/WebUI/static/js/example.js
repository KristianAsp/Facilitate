
var x = document.getElementsByClassName("ticket-column");
var availableTags = fetchUsersForProject()

dragula(Array.from(x), {
          moves: function(el, container, handle){
            var res = $(el).is('.unique-ticket')
            return res
          }
        })
        .on('drop', function (el, target, source) {
          if(target.id == "BL"){
            updateStateOfTask(el.id, target.id)
            shouldUpdateConcurrently = true;
            return
          }
          var cancel = false;
          shouldUpdateConcurrently = true;
          $("#cancelUpdate").click(function(){
            target.removeChild(el);
            source.appendChild(el);
            cancel = true;
          });

          $("#update").click(function(){
            if(!cancel){
              updateStateOfTask(el.id, target.id);
              $('#myModal').modal('hide');
            }
          });

          $('#myModal').modal('show');
          $('#myModal').on('shown.bs.modal', function() {
            $("#myInput").val(el.id);
            $("#assigned_to").autocomplete({
              source: availableTags,
              });
          })
         })

         .on('drag', function (el) {
           shouldUpdateConcurrently = false;
          });

function lol(id) {
  return document.getElementById(id);
}


function validateUpdate(){
  return true;
}



function updateClubdays(button){

}
