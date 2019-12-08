function ajax(url, type, data, sfunc, efunc) {
    $.ajax({
        url: url,
        type: type,
        contentType: "application/json",
        data: data, 
        success: sfunc(response), 
        error: efunc(error)
    });
}