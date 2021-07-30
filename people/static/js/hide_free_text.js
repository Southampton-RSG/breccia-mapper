function hasOption(select, option) {
    var exists = false;
    for (var i = 0; i < select.options.length; i++) {
        if (select.options[i].text.toLowerCase().startsWith(option)) return true;
    }

    return false;
}

function setFreeTextState(select, freeTextField) {
    var other_selected = false;
    for (var i = 0; i < select.selectedOptions.length; i++) {
        if (select.selectedOptions[i].text.toLowerCase().startsWith('other')) {
            other_selected = true;
        }
    }

    if (other_selected) {
        freeTextField.show();
    } else {
        freeTextField.hide();
    }
}

$(document).ready(function () {
    $('select').each(function (index, element) {
        if (hasOption(element, 'other')) {
            var freeTextField = $('#' + element.id + '_free').parent();
            setFreeTextState(element, freeTextField);

            $('#' + element.id).on('change', function (event) {
                setFreeTextState(event.target, freeTextField);
            });
        }
    })
});
