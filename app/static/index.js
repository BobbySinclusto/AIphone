function pop(asdf) {
    var b = document.getElementById('imagepreview');
    b.src = document.getElementById(asdf).src;
    $('#imagemodal').modal('show');
}
