$(function() {
    function get_faces() {
        $("#sample-faces").addClass('hidden');
        $.getJSON( "/faces?n=6", function( data ) {
            $.each(data, function(index, face) {
                var date = $.format.date(face['date'], "d MMM yyyy");
                $("#sample-face-" + index + " > a > img").attr("src", face['image_url']);
                $("#sample-face-" + index + " > a").attr("href", face['article_url']).attr('title', date + ", " + face['title']);
            });
            $('[data-toggle="tooltip"]').tooltip();
            $("#sample-faces").removeClass('hidden');
        });
    }
    $("#load-faces").click(get_faces);
    get_faces();
});