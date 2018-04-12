
var x = document.getElementsByClassName("ticket-column");
var availableTags = fetchUsersForProject()

function populateAvailableTags(){
  $(".assigned_to").autocomplete({
    source: availableTags,
  });
}
dragula(Array.from(x), {
          moves: function(el, container, handle){
            var res = $(el).is('.unique-ticket')
            return res
          }
        })
        .on('drop', function (el, target, source) {
          if(target.id == "BL" || target.id == "C"){
            updateStateOfTask(el.id, target.id)
            shouldUpdateConcurrently = true;
            return
          }
          $('#myModal').modal('show');



          $('#myModal').on('shown.bs.modal', function() {
            $(".assigned_to").autocomplete({
              source: availableTags,
              });
              $("#update").off("click");
              $(".dismiss-modal").off("click");

              $("#update").click(function(){
                updateStateOfTask(el.id, target.id);
                shouldUpdateConcurrently = true;
                $('#myModal').modal('hide');
              });

              $(".dismiss-modal").click(function(){
                source.appendChild(el);
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
