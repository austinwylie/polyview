var transparentDemo = true;
var fixedTop = false;

$(window).scroll(function(e) {
    oVal = ($(window).scrollTop() / 170);
    $(".blur").css("opacity", oVal);
    
});

$(document).ready(function(){
   sectionTable = $(".section-table");
   if(sectionTable.length) stripeTables(sectionTable);
});


//Given an array of tables stripes them grouping by section number
function stripeTables(tables){
    var stripeColor = "#F9F9F9";
    var stdColor = "#FFFFFF";

    //Each table
    tables.each(function(i, table){
        var previousColor = 1;
        var previousSection = undefined;
        //Each row of that table
        $.each(table.rows, function(i, row){
            //Get the section string
            var section = $(row).find(".section").html();
            //If this section is different from last, swap colors
            if (section != previousSection) {
                previousColor = 1 - previousColor;
            }
            //Update previous section
            previousSection = section;

            //Set background color
            if (previousColor) {
                $(row).css("background", stripeColor);
            }
            else{
                $(row).css("background", stdColor);
            }
        });

    });
}

$( "#polyFilter" ).change(function() {
    selected = $( "#polyFilter option:selected" ).text();
    courses = $.map(selected.split("/"), function(val){return $.trim(val);})

    //Iterate through table
    $("#polyTable > tbody > tr").each(function() {
        course = $(this).find(".polyCourse").text();
        if (selected == "All"){
            $(this).removeClass("hidden");
        }
        else if ($.inArray(course, courses) != -1){
            $(this).removeClass("hidden");
        }
        else {
            $(this).addClass("hidden");
        }
    });
});