$( document ).ready(function() {
    console.log("I'm ready")
    
});

$("#submitAuth").click(function(event) {
    event.preventDefault();
    $("#authorizeForm").submit();		
});

$("#submitGmail").click(function(event) {
    event.preventDefault();
    $("#gmailForm").submit();		
});

$("#submitUpload").click(function(event) {
    event.preventDefault();
    $("#uploadForm").submit();		
});

$('.password-group').children(".fa").click(function() {
    $(this).toggleClass("fa-eye fa-eye-slash");
    var type = $('.pass').attr("type");
    if(type === 'password'){
        $('.pass').attr("type", "text");
    } else {
        $('.pass').attr("type", "password");
    }
});