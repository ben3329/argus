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
                form.method = 'put'

                // Set the form fields to the appropriate values
                var nameField = $('#id_name');
                var languageField = $('#id_language');
                var codeField = $('#id_code');
                var authorityField = $('#id_authority');
                var outputTypeField = $('#id_output_type');
                var noteField = $('#id_note');

                nameField.val(response['name']);
                languageField.val(response['language']);
                codeField.val(response['code']);
                authorityField.val(response['authority']);
                outputTypeField.val(response['output_type']);
                noteField.val(response['note']);
            },
            error: function (xhr, status, error) {
                alert("Error: " + error)
            }
        });
    });
});
