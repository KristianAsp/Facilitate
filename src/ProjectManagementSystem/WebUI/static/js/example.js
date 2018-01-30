
var x = document.getElementsByClassName("ticket-column");

dragula(Array.from(x))
        .on('drop', function (el, target, source) {
          updateStateOfTask(el.id, target.id)
         });

function lol(id) {
  return document.getElementById(id);
}
