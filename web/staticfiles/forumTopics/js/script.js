$(document).ready(function () {

   var minDate=yearAgo();
   $('#yesterday').on('click', function () {

       var dateFromElem;
       var elem=$("#main_date_field");
       if (!elem.val()){
          dateFromElem=elem.attr("placeholder").split(".");
       }else {
          dateFromElem=elem.val().split(".");
       }
       var d=new Date(dateFromElem[2],dateFromElem[1]-1, dateFromElem[0]);
       d.setDate(d.getDate()-1);
       var minDateToCompare=new Date(minDate);
       minDateToCompare.setDate(minDateToCompare.getDate()-1);
       if (d>minDateToCompare){
         errorMessageHide();
         elem.val(dateStringView(d));
         updateTopicsByDate();
       }
       else {
           errorMessageShow("Минимальная дата "+dateStringView(minDate));
       }

    });
    $('#tomorrow').on('click', function () {
       var max=new Date();
       var dateFromElem;
       var elem=$("#main_date_field");
       if (!elem.val()){
          dateFromElem=elem.attr("placeholder").split(".");
       }else {
          dateFromElem=elem.val().split(".");
       }
       var d=new Date(dateFromElem[2],dateFromElem[1]-1, dateFromElem[0]);
       d.setDate(d.getDate()+1);
       if (d<max){
         errorMessageHide();
         elem.val(dateStringView(d));
         updateTopicsByDate();
       }
       else {
           errorMessageShow("Максимальная дата "+dateStringView(max));
       }

    });

  $(window).scroll(function() {

    elem = $(".active_block").find( $(".title_block") );
    cont=$(".active_block").find( $(".title-container") );
    if($(this).scrollTop() > 200) {
        setTimeout(function(){
            elem.addClass("fixed");
            $(".container-fixed-inner").append(elem);
        }, 100);

    }
    else{
        elem=$(".container-fixed-inner").find( $(".title_block"));
        setTimeout(function(){
             elem.removeClass("fixed");
             $(".active_block").find( $(".title-container")).append(elem);
        }, 100);

    }
  });

    var o, n;
      $(".title_block").on("click", function() {
        if($(".container-fixed-inner").has($(".title_block"))){
         elem=$(".container-fixed-inner").find( $(".title_block"));
         elem.removeClass("fixed");
         $(".active_block").find( $(".title-container")).append(elem);

        o = $(this).parents(".accordion_item");
        n = o.find(".info");
        o.hasClass("active_block") ? (o.removeClass("active_block"),
            n.slideUp()) : (o.addClass("active_block"),  n.stop(!0, !0).slideDown(),
            o.siblings(".active_block").removeClass("active_block").children(
              ".info").stop(!0, !0).slideUp());
        $('body,html').animate({scrollTop: 0}, 200);
        }

      });

    $(".tab-toggle-button").on("click", function () {
        if (!$(this).parent().hasClass("active") &&
            !$(this).parent().hasClass("disabled")) {
            $(".tab-toggle-button" ).each(function() {
                $( this ).parent().removeClass("active");
            });
            $(this).parent().addClass("active");

            updateTabContent($(this));
        }

    });

  $("#main_date_field").change(function () {
      var value=$(this).val();
      var myDatepicker = $(this).datepicker().data('datepicker');
      myDatepicker.hide();
      errorMessageHide();
      var dateFromElem=value.split(".");
      var pattern = /^([0-9]{1,2})\.([0-9]{1,2})\.([0-9]{4})$/i;
      if((value.search(pattern)==-1) ){
         errorMessageShow("Введите правильную дату в формате \"дд.мм.ГГГГ\" или \"д.м.ГГГГ\"");
      }
      else {

          var d=new Date(dateFromElem[2],dateFromElem[1]-1, dateFromElem[0]);
          var minDAteToCompare=new Date(minDate.getFullYear(),
              minDate.getMonth(),minDate.getDate());
          var max=new Date();
          if (d<minDAteToCompare){
               errorMessageShow("Минимальная дата "+dateStringView(minDate));
          } else if(d>max){
               errorMessageShow("Максимальная дата "+dateStringView(max));
          } else {
              $(this).val(value);
              updateTopicsByDate();
              $(this).val("");
          }
      }
  });

  $(function () {
    $('[data-toggle="tooltip"]').tooltip()
  });

  $('.msgpost-spoiler-txt').hide();

  $('.msgpost-spoiler-hd').click(function(){
            var top = $(this).closest($(".message")).offset().top;
            var navbarHeigth=$('.navbar').height();
            target=$(this).parent().next();
            if(target.css('display')=='none'){
               target.show();
               $('body,html').animate({scrollTop: top-navbarHeigth}, 100);
            }
            else {
                $('body,html').animate({scrollTop: top-navbarHeigth}, 100);
                target.hide();
            }

		});

});
