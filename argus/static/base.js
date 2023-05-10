function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

$('#createNewButton').on('click', function (e) {
    e.preventDefault();
    $('#formInModal').attr('action', mainApi);
    $('#formInModal').attr('method', 'post');
    $('#formInModal')[0].reset();
    $('#createButton').text('Create')
    $('#warningMessage').text('').addClass('d-none');
});

$(document).ready(function () {
    $('#formInModal').submit(function (event) {
        event.preventDefault();
        var form = $(this);
        $.ajax({
            url: form.attr('action'),
            type: form.attr('method'),
            data: form.serialize(),
            beforeSend: function (xhr) {
                if (this.type == 'PUT' || this.type  == 'PATCH') {
                    xhr.setRequestHeader("X-CSRFToken", getCookie("csrftoken"));
                }
            },
            success: function (response) {
                $('#createModal').modal('hide');
                location.reload();
            },
            error: function (xhr, status, error) {
                var response = xhr.responseJSON;
                $.each(response, function (field, messages) {
                    var fieldId = '#id_' + field;
                    $(fieldId).addClass('is-invalid');
                    $(fieldId + ' + .invalid-feedback').text(messages);
                });
                $('#warningMessage').text('Please correct the errors.').removeClass('d-none');
            }
        });
    });
});

$(document).ready(function () {
    const checkboxes = $('[name="object-id"]');
    const checkAllCheckbox = $('#check-all');
    const deleteButton = $('#deleteButton');

    function updateDeleteButton() {
        let checked = false;
        checkboxes.each(function () {
            if (this.checked) {
                checked = true;
                return false;
            }
        });
        deleteButton.prop('disabled', !checked);
    }

    function updateCheckAllCheckbox() {
        let allChecked = true;
        checkboxes.each(function () {
            if (!this.checked) {
                allChecked = false;
                return false;
            }
        });
        checkAllCheckbox.prop('checked', allChecked);
    }

    updateDeleteButton();
    updateCheckAllCheckbox();

    checkboxes.on('change', function () {
        updateDeleteButton();
        updateCheckAllCheckbox();
    });

    checkAllCheckbox.on('change', function () {
        checkboxes.prop('checked', $(this).prop('checked'));
        updateDeleteButton();
    });
});

$('#deleteButton').click(function () {
    const checkedValues = $('input[name="object-id"]:checked').map(function () {
        return $(this).val();
    }).get();
    const message = "Are you sure you want to delete the selected?";
    const confirmed = window.confirm(message);
    if (confirmed) {
        $.ajax({
            url: mainApi + 'delete_bulk',
            type: 'delete',
            data: {
                'ids': checkedValues
            },
            beforeSend: function (xhr) {
                xhr.setRequestHeader("X-CSRFToken", getCookie("csrftoken"));
            },
            success: function (response) {
                location.reload();
            },
            error: function (xhr, status, error) {
                alert('Error: ' + error);
            }
        });
    }
});

$(document).ready(function () {
    $("#check-all").click(function () {
        $(".check-item").prop('checked', $(this).prop('checked'));
    });
});
