$( document ).ready(function() {
    console.log("I'm ready")
});

$("#submitAuth").click(function(event) {
    event.preventDefault();
    $("#authorizeForm").submit();		
});