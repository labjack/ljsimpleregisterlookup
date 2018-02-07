var displayingInputControls = false;

function renderInline(msg, node) {
    node.contents().find("html").html(
        $.parseHTML(
            msg,
            node.contents(),
            true
        )
    );
};

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
                url: "/error_scribe",
                data: { input: $('#input-code-area').val() }
            }).done(function( msg ) {
                $('#output-code-area').val(msg);
                $('#output-section').slideDown();
                $('#input-section #waiting').hide();
                $('#input-section #controls').fadeIn();
                renderInline(msg, $('#rendered-output-code-context-large'));
                renderInline(msg, $('#rendered-output-code-context-small'));
            });
        });
    });
});
