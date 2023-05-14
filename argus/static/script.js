$(function () {
    $('.edit-script').on('click', function (e) {
        e.preventDefault();
        var scriptId = $(this).data('script-id');
        $.ajax({
            url: mainApi + scriptId + '/',
            type: 'GET',
            success: function (response) {
                var modal = new bootstrap.Modal(document.getElementById('createModal'), {
                    keyboard: false,
                    focus: true
                });
                modal.show();
                $('#createButton').text('Update');
                $('#warningMessage').text('').addClass('d-none');

                // Set the form action URL to the asset update view
                var form = document.getElementById('formInModal');
                form.action = mainApi + scriptId + '/';
                form.method = 'patch'

                // Set the form fields to the appropriate values
                var nameField = $('#id_name');
                var languageField = $('#id_language');
                var codeField = $('#id_code');
                var parametersField = $('#id_parameters');
                var fieldsField = $('#id_fields');
                var outputTypeField = $('#id_output_type');
                var noteField = $('#id_note');
                
                nameField.val(response['name']);
                languageField.val(response['language']);
                codeField.val(response['code']);
                parametersField.val(response['parameters'])
                fieldsField.val(response['fields'])
                outputTypeField.val(response['output_type']);
                noteField.val(response['note']);

                $('.param-input-group').remove();
                response['parameters'].forEach(function(parameter) {
                    var inputGroup = '<div class="input-group mb-1 param-input-group">'
                        + '<input type="text" name="parameters[]" class="form-control col-10" value="' + parameter + '" readonly>'
                        + '<button class="btn btn-outline-secondary col-2 param-button-remove" type="button">-</button>'
                        + '</div>';

                    $(inputGroup).insertBefore($('#parameters-feedback'));
                });
                $('.fields-input-group').remove();
                response['fields'].forEach(function(field) {
                    var inputGroup = '<div class="input-group mb-1 fields-input-group">'
                        + '<input type="text" name="fields[]" class="form-control col-10" value="' + field + '" readonly>'
                        + '<button class="btn btn-outline-secondary col-2 field-button-remove" type="button">-</button>'
                        + '</div>';

                    $(inputGroup).insertBefore($('#fields-feedback'));
                });
            },
            error: function (xhr, status, error) {
                alert("Error: " + error)
            }
        });
    });
});

$(document).ready(function () {
    $(document).on('click', '.param-button-addon', function () {
        var inputValue = $('input[name="tmp-parameters[]"]').val();
        if (inputValue) {
            var inputGroup = '<div class="input-group mb-1 param-input-group">'
                + '<input type="text" name="parameters[]" class="form-control col-10" value="' + inputValue + '" readonly>'
                + '<button class="btn btn-outline-secondary col-2 param-button-remove" type="button">-</button>'
                + '</div>';

            $(inputGroup).insertBefore($('#parameters-feedback'));
            $('input[name="tmp-parameters[]"]').val('');
        }
    });

    $(document).on('click', '.param-button-remove', function () {
        $(this).parent().remove();
    });
});

$(document).ready(function () {
    $(document).on('click', '.fields-button-addon', function () {
        var inputValue = $('input[name="tmp-fields[]"]').val();
        if (inputValue) {
            var inputGroup = '<div class="input-group mb-1 fields-input-group">'
                + '<input type="text" name="fields[]" class="form-control col-10" value="' + inputValue + '" readonly>'
                + '<button class="btn btn-outline-secondary col-2 field-button-remove" type="button">-</button>'
                + '</div>';

            $(inputGroup).insertBefore($('#fields-feedback'));
            $('input[name="tmp-fields[]"]').val('');
        }
    });

    $(document).on('click', '.field-button-remove', function () {
        $(this).parent().remove();
    });
});


$('#createNewButton').on('click', function (e) {
    e.preventDefault();
    $('#formInModal').attr('action', mainApi);
    $('#formInModal').attr('method', 'post');
    $('#formInModal')[0].reset();
    $('#createButton').text('Create')
    $('#warningMessage').text('').addClass('d-none');
    $('.param-input-group').remove();
    $('.fields-input-group').remove();
});