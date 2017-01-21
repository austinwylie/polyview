/**
 * Created by twoods0129 on 3/6/15.
 */

function responsiveness(){
    $("#faq-sidebar").removeClass("affix");
    $("#faq-content").css("padding-left", "15px");
}

function unresponsiveness(){
    $("#faq-sidebar").addClass("affix");
    $("#faq-content").css("padding-left", "40px");
}

function respond(e){
    //Pixel value at which bootstrap-md columns kick in
    if (e.width() < 992) {
        responsiveness();
    }
    else{
        unresponsiveness();
    }
}

$( window ).resize(function(e) {
    respond($(this));
});

$( document ).ready(function(e) {
    respond($(this));
});