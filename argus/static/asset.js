function setDefaultPort(accessType) {
    if (!$('#id_port').val()) {
        if (accessType.substr(0, 4) === 'ssh_') {
            $('#id_port').val('22');
        }
    }
}

function setAccessCredential(select_id = -1) {
    $.ajax({
        url: accessCredentialApi + 'simple',
        type: 'GET',
        beforeSend: function (xhr) {
            xhr.setRequestHeader("X-CSRFToken", getCookie("csrftoken"));
        },
        success: function (response) {
            var accessCredentials = response;
            var select = $('#id_access_credential');
            select.empty();
            if (select_id == '') {
                var option = $('<option>').val("").text("---------");
                select.append(option);
                option.attr('selected', true);
            }
            var set_selected = false;
            $.each(accessCredentials, function (index, accessCredential) {
                var option = $('<option>').val(accessCredential.id).text(accessCredential.name);
                option.attr('data-access-type', accessCredential.access_type)
                if (select_id == accessCredential.id) {
                    option.attr('selected', true);
                    set_selected = true;
                }
                select.append(option);
            });
            var select = $('#id_access_credential');
            var options = select.find('option');
            if (set_selected === false) {
                options.first().prop('selected', true);
                setDefaultPort(options.first().data('access-type'));
            }
        },
        error: function (xhr, status, error) {
            $('#warningMessage').text(error).removeClass('d-none');
        }
    });
}

$('#createNewButton').on('click', function (e) {
    setAccessCredential();
    e.preventDefault();
    $('#formInModal').attr('action', mainApi);
    $('#formInModal').attr('method', 'post');
    $('#formInModal')[0].reset();
    $('#createButton').text('Create')
    $('#warningMessage').text('').addClass('d-none');
});

$(function () {
    $('.edit-asset').on('click', function (e) {
        e.preventDefault();
        var assetName = $(this).data('asset-name');
        var assetIp = $(this).data('asset-ip');
        var assetPort = $(this).data('asset-port');
        var assetAssetType = $(this).data('asset-asset-type');
        var assetAccessCredential = $(this).data('asset-access-credential');
        var assetNote = $(this).data('asset-note');
        var assetId = $(this).data('asset-id');

        var modal = new bootstrap.Modal(document.getElementById('createModal'), {
            keyboard: false,
            focus: true
        });
        modal.show();

        $('#createButton').text('Update');
        $('#warningMessage').text('').addClass('d-none');

        setAccessCredential(assetAccessCredential);

        // Set the form action URL to the asset update view
        var form = document.getElementById('formInModal');
        form.action = mainApi + assetId + '/';
        form.method = 'patch'

        // Set the form fields to the appropriate values
        var nameField = $('#id_name');
        var ipField = $('#id_ip');
        var portField = $('#id_port');
        var assetTypeField = $('#id_asset_type');
        var accessCredentialField = $('#id_access_credential');
        var noteField = $('#id_note');

        nameField.val(assetName);
        ipField.val(assetIp);
        portField.val(assetPort);
        assetTypeField.val(assetAssetType);
        accessCredentialField.val(assetAccessCredential);
        noteField.val(assetNote);
    });
});

$(document).ready(function () {
    $('#id_access_credential').on('change', function () {
        var accessCredentialId = $(this).val();
        if (accessCredentialId === '') {
            $('#id_port').val('');
        } else {
            var selectedOption = $(this).find('option:selected');
            var accessType = selectedOption.data('access-type');
            setDefaultPort(accessType);
        }
    });
});

$('#createNewButton').on('click', function (e) {
    e.preventDefault();
    $('#formInModal').attr('action', mainApi);
    $('#formInModal').attr('method', 'post');
    $('#formInModal')[0].reset();
    $('#createButton').text('Create')
    $('#createButton').attr('disabled', true);
    $('#warningMessage').text('').addClass('d-none');
});


$(document).ready(function () {
    $(document).on('click', '.test-button-addon', function () {
        var ip = $('#id_ip').val()
        var port = $('#id_port').val()
        var access_credential = $('#id_access_credential').find('option:selected').val()
        var data = {'ip': ip, 'port': port, 'access_credential': access_credential}
        $.ajax({
            url: mainApi + 'test/',
            type: 'POST',
            data: JSON.stringify(data),
            contentType: 'application/json',
            beforeSend: function (xhr) {
                xhr.setRequestHeader("X-CSRFToken", getCookie("csrftoken"));
            },
            success: function (response) {
                $('#createButton').removeAttr('disabled');
                $('#warningMessage').text('').addClass('d-none');
            },
            error: function (xhr, status, error) {
                var response = xhr.responseJSON['error_msg'];
                $('#warningMessage').text(response).removeClass('d-none');
            }
        });
    });
});