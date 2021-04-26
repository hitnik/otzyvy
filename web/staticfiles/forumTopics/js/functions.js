function yearAgo () {
       var now = new Date();
       var oneYr = new Date();
       oneYr.setYear(now.getFullYear() - 1);
       return oneYr;
   };

function updateTopicsByDate() {
    dateFromElem=$("#main_date_field").val().split(".");
    url="/forums/1/";
    var i;
    for (i = dateFromElem.length-1; i >=0; --i) {
        url+=dateFromElem[i];
        if(i>0){
            url+="/"
        }
    }
    $.ajax({
            type: "GET",
            url: url,
            dataType: "json",
            cache: false,
            success: function(resp){
                window.location.replace(url);
            },
             error : function(resp) {
                errorMessageShow("Введите правильную дату в формате \"дд.мм.ГГГГ\" или \"д.м.ГГГГ\"");

            }
       });

};

function updateTabContent(e) {
    var date;
        if($("#main_date_field").val()){
           date=$("#main_date_field").val();
        }
        else date=$("#main_date_field").attr("placeholder") ;
    $.ajax({
            type: "GET",
            url: "/forums/topics/",
            data:{'siteId':e.attr('data-v'), 'dateString':date},
            dataType: "json",
            cache: false,
            success: function(data){
                 $("#tabContent").empty();
                 $("#tabContent").append(data.content);
            }
       });
};

function errorMessageShow(str) {
    $("#error_container").html("<strong>Внимание!</strong> "+str);
    $("#error_container").show("slow");
    setTimeout(function() { $("#error_container").hide('slow'); }, 5000);
};

function errorMessageHide() {
    $("#error_container").hide('slow');
};

function dateStringView(date) {
    var mm=((date.getMonth() + 1)>9 ? '' : '0') + (date.getMonth() + 1);
    var dd= (date.getDate()>9 ? '' : '0') + date.getDate();
    dateString =dd+"."+mm+"."+date.getFullYear();
    return dateString;
};
