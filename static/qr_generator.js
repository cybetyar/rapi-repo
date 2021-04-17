    var new_qrcode = String(document.getElementById('new_qrcode').innerHTML);
    $(function() {
        $(".qr_code").attr("src", "https://chart.googleapis.com/chart?cht=qr&chl=" + new_qrcode + "&chs=160x160&chld=L|0");
    });
