var displayingInputControls = false;

$(window).load(function () {
    $('#catchphrase').hide().delay(200).slideDown();
    $('#input-section #controls').hide();
    
    $('#input-code-area').focus(function (e) {
        $('#input-section #title').fadeOut(function () {
            $('#input-section #controls').fadeIn();
        });
    });

    $('#generate-button').click(function () {
        $('#input-section #controls').fadeOut(function () {
            $('#input-section #waiting').fadeIn();

            $.ajax({
                type: "POST",
                url: "/scribe",
                data: { input: $('#input-code-area').val() }
            }).done(function( msg ) {
                $('#output-code-area').val(msg);
                $('#output-section').slideDown();
                $('#input-section #waiting').hide();
                $('#input-section #controls').fadeIn();
                div = document.getElementById('rendered-output-code-context-large');
                div.innerHTML = msg;
                div = document.getElementById('rendered-output-code-context-small');
                div.innerHTML = msg;
            });
        });
    });
});
