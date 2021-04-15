var max_id = parseInt(document.getElementById('max_id').innerHTML);
var current_id = max_id + 1;

$(function() {
    $(".qr_code").attr("src", "https://chart.googleapis.com/chart?cht=qr&chl=" + current_id + "&chs=160x160&chld=L|0");
});
