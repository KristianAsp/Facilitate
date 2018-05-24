var flag;
var updateSuccess = function (response) {
    var notification_box = $(nfBoxListClassSelector);
    var notifications = response.notifications;

    function compare(a,b) {
      if (a.id < b.id)
        return -1;
      if (a.id > b.id)
        return 1;
      return 0;
    }

    notifications.sort(compare);

    $.each(notifications, function (i, notification) {
        notification_box.prepend(notification.html);
    });

    var notifications_count = notifications.length;
    var current_count = function(){
      if($('.mark-all-notifications').data('badge')){
        return $('.mark-all-notifications').data('badge');
      }else {
        return 0
      }
    }

    var total = notifications_count + current_count();
    if(total != $('.mark-all-notifications').data('badge') && total != 0){
      $('.mark-all-notifications').data('badge', total);
      $('.mark-all-notifications').attr('data-badge', total);
    }


};
