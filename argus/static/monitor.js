function fetchAsset(select_id) {
    $.ajax({
        url: assetApi + 'simple',
        type: 'GET',
        beforeSend: function (xhr) {
            xhr.setRequestHeader("X-CSRFToken", getCookie("csrftoken"));
        },
        success: function (response) {
            var asset_list = response;
            var select = $('#id_asset');
            select.empty();
            if (select_id == null) {
                var option = $('<option>').val("").text("---------");
                select.append(option);
                option.attr('selected', true);
            }
            var set_selected = false;
            $.each(asset_list, function (index, asset) {
                var option = $('<option>').val(asset.id).text(asset.name);
                if (select_id == asset.id) {
                    option.attr('selected', true);
                    select.attr('disabled', true);
                }
                select.append(option);
            });
        },
        error: function (xhr, status, error) {
            $('#warningMessage').text(error).removeClass('d-none');
        }
    });
}

function fetchFields(fields, scrape_fields) {
    $('.scrape_fields-group').remove();
    var colCount = 0;
    var row = $('<div class="row scrape_fields-group"></div>');
    if (Array.isArray(scrape_fields)) {
        $('#id_scrape_fields').attr('disabled', true);
    }
    fields.forEach(function(field) {
        if (Array.isArray(scrape_fields)) {
            if (scrape_fields.includes(field)){
                var fieldsGroup = '<div class="col-6">'
                                + '<input type="checkbox" checked disabled class="mx-1 scrape_fields" id="id_scrape_fields.' + field + '" name="scrape_fields[]" value="' + field + '">'
                                + '<label for="id_scrape_fields.' + field +'">' + field + '</label>'
                                + '</div>';
            } else {
                var fieldsGroup = '<div class="col-6">'
                                + '<input type="checkbox" disabled class="mx-1 scrape_fields" id="id_scrape_fields.' + field + '" name="scrape_fields[]" value="' + field + '">'
                                + '<label for="id_scrape_fields.' + field +'">' + field + '</label>'
                                + '</div>';
            }
        } else {
            var fieldsGroup = '<div class="col-6">'
                            + '<input type="checkbox" class="mx-1 scrape_fields" id="id_scrape_fields.' + field + '" name="scrape_fields[]" value="' + field + '">'
                            + '<label for="id_scrape_fields.' + field +'">' + field + '</label>'
                            + '</div>';
        }
        if (colCount % 2 == 0) { // 새로운 행을 시작
            row = $('<div class="row scrape_fields-group"></div>');
            $(row).insertBefore($('#scrape_fields-feedback'));
        }
        $(row).append($(fieldsGroup));
        colCount++;
    });
}

function fetchParameters(parameters, scrape_parameters) {
    $('.scrape_parameters-group').remove();
    if (scrape_parameters) {
        parameters.forEach(function(parameter) {
            if (parameter in scrape_parameters){
                var parametersGroup = '<div class="input-group mb-1 scrape_parameters-group">'
                    + '<span class="input-group-text col-4">' + parameter + '</span>'
                    + '<input type="text" name="scrape_parameters[' + parameter + ']" '
                    + 'value="'+ scrape_parameters[parameter] +'"'
                    + 'class="form-control col-8" id="id_scrape_parameters.' + parameter + '" readonly>'
                    + '</div>';
            } else {
                var parametersGroup = '<div class="input-group mb-1 scrape_parameters-group">'
                    + '<span class="input-group-text col-4">' + parameter + '</span>'
                    + '<input type="text" name="scrape_parameters[' + parameter + ']" '
                    + 'class="form-control col-8" id="id_scrape_parameters.' + parameter + '" readonly>'
                    + '</div>';
            }
            $(parametersGroup).insertBefore($('#scrape_parameters-feedback'));
        });
    } else {
        parameters.forEach(function(parameter) {
            var parametersGroup = '<div class="input-group mb-1 scrape_parameters-group">'
                + '<span class="input-group-text col-4">' + parameter + '</span>'
                + '<input type="text" name="scrape_parameters[' + parameter + ']" '
                + 'class="form-control col-8" id="id_scrape_parameters.' + parameter + '">'
                + '</div>';
            $(parametersGroup).insertBefore($('#scrape_parameters-feedback'));
        });
    }
}

function initUserDefinedScript(){
    $('#id_script').remove();
    var user_defined_script_select = '<div class="row mb-3 mx-2" id="id_script">'
            + '<div class="col-4">'
            +   '<label for="id_user_defined_script" class="form-label">User Defined Script</label>'
            + '</div>'
            + '<div class="col-8">'
            +   '<select name="user_defined_script" class="form-control" id="id_user_defined_script">'
            +   '</select>'
            +   '<div class="text-danger invalid-feedback"></div>'
            + '</div>'
        + '</div>'
    $(user_defined_script_select).insertBefore($('#id_scrape_category').parent().parent().next());
    $('#id_user_defined_script').on('change', function () {
        var selectedOption = $(this).find('option:selected');
        var fields = selectedOption.data('fields');
        var parameters = selectedOption.data('parameters');
        fetchFields(fields);
        fetchParameters(parameters);
    });
}

function fetchUserDefinedScript(select_id, scrape_fields, scrape_parameters) {
    initUserDefinedScript();
    $.ajax({
        url: scriptApi + 'simple',
        type: 'GET',
        beforeSend: function (xhr) {
            xhr.setRequestHeader("X-CSRFToken", getCookie("csrftoken"));
        },
        success: function (response) {
            var script_list = response;
            var select = $('#id_user_defined_script');
            if (select_id == null) {
                var option = $('<option>').val("").text("---------");
                select.append(option);
                option.attr('selected', true);
            }
            $.each(script_list, function (index, script) {
                var option = $('<option>').val(script.id).text(script.name);
                if (select_id == script.id) {
                    option.attr('selected', true);
                    fetchFields(script.fields, scrape_fields);
                    fetchParameters(script.parameters, scrape_parameters);
                }
                option.attr('data-fields', JSON.stringify(script.fields));
                option.attr('data-parameters', JSON.stringify(script.parameters));
                select.append(option);
            });
        },
        error: function (xhr, status, error) {
            $('#warningMessage').text(error).removeClass('d-none');
        }
    });
}

$(document).ready(function () {
    // 카테고리 수정
    $('#id_scrape_category').on('change', function () {
        var scrapeCategoryId = $(this).val();
        if (scrapeCategoryId === 'user_defined_script') { // 사용자 정의 스크립트 선택
            fetchUserDefinedScript();
            $('.scrape_fields-group').remove();
            $('.scrape_parameters-group').remove();
        } else {
            $('#id_script').remove();
            var selectedOption = $(this).find('option:selected');
            var fields = selectedOption.data('fields');
            var parameters = selectedOption.data('parameters');
            fetchFields(fields);
            fetchParameters(parameters);
        }
    });
});

function getRecipients(inputText) {
    var suggestionRecipients = $('#suggestionRecipients');
    suggestionRecipients.empty();
    $.ajax({
        url: recipientsApi + '?search=' + inputText,
        type: 'GET',
        beforeSend: function (xhr) {
            xhr.setRequestHeader("X-CSRFToken", getCookie("csrftoken"));
        },
        success: function (response) {
            response.results.forEach(function(item) {
                if (recipientsArray.includes(item.id)){
                    return;
                }
                var listItem = $('<a>')
                    .addClass('dropdown-item')
                    .attr('data-id', item.id)
                    .text(item.username);
                suggestionRecipients.append(listItem);
            });
            suggestionRecipients.css('display', 'block');
        },
        error: function (xhr, status, error) {
            $('#warningMessage').text(error).removeClass('d-none');
        }
    });
}

function setRecipient(id, username) {
        var inputGroup = '<div class="input-group recipients-input-group form-control">'
                + '<input type="hidden" name="recipients[]" value="' + id + '">'
                + '<span class="input-group-text col-10">' + username + '</span>'
                + '<button class="btn btn-outline-secondary col-2 recipients-button-remove" type="button">-</button>'
                + '</div>';
        $('#id_recipients_container').append(inputGroup);

}

$(document).ready(function() {
    $('#id_recipients').on('input', function() {
        var inputText = $(this).val();
        if (inputText) {
            getRecipients(inputText);
        } else {
            var suggestionRecipients = $('#suggestionRecipients');
            suggestionRecipients.empty();
            suggestionRecipients.css('display', 'none');
        }
    });
    $('#suggestionRecipients').on('click', '.dropdown-item', function() {
        var username = $(this).text();
        var id = $(this).data('id');
        recipientsArray.push(id);
        var selectedRecipient = $(this).parent();
        selectedRecipient.empty();
        selectedRecipient.css('display', 'none');
        setRecipient(id, username);
        $('input[name="tmp-recipients[]"]').val('');
    });
    $(document).on('click', '.recipients-button-remove', function () {
        var id = $(this).parent().find('input[type="hidden"]').val();
        recipientsArray = recipientsArray.filter(function(element) {
            return element != id;
        });
        $(this).parent().remove();
    });
});

$(function () {
    $('.edit-monitor').on('click', function (e) {
        e.preventDefault();
        var monitorId = $(this).data('monitor-id');
        $.ajax({
            url: mainApi + monitorId + '/',
            type: 'GET',
            success: function (response) {
                var modal = new bootstrap.Modal(document.getElementById('createModal'), {
                    keyboard: false,
                    focus: true
                });
                modal.show();
                $('#formInModal')[0].reset();
                $('#createButton').text('Update');
                $('#warningMessage').text('').addClass('d-none');

                var form = document.getElementById('formInModal');
                form.action = mainApi + monitorId + '/';
                form.method = 'patch'

                var nameField = $('#id_name');
                var intervalField = $('#id_interval');
                var reportTimeField = $('#id_report_time');
                var noteField = $('#id_note');

                
                nameField.val(response['name']);
                nameField.attr('disabled', true);
                intervalField.val(response['interval']);
                reportTimeField.val(response['report_time']);
                noteField.val(response['note']);
                response['report_list'].forEach(function(report) {
                    $('#id_report_list\\.' + report).prop('checked', true);
                });
                recipientsArray = [];
                $('#id_recipients_container').empty();
                $.each(response['recipients'], function(index, id) {
                    setRecipient(id, response['recipients_username'][index])
                    recipientsArray.push(id);
                });
                fetchAsset(response['asset']);
                $('#id_scrape_category').val(response['scrape_category']);
                $('#id_scrape_category').attr('disabled', true);
                if (response['scrape_category'] == 'user_defined_script') {
                    // 추후 필드 및 파라미터 수정 지원을 위해 fetchUserDefinedScript를 사용하여 user_deinfed_script 전체값을 가져온다.
                    fetchUserDefinedScript(response['user_defined_script'], response['scrape_fields'], response['scrape_parameters']);
                    $('#id_user_defined_script').attr('disabled', true);
                } else {
                    $('#id_script').remove();
                    var selectedScrape = $("#id_scrape_category option:selected");
                    fetchFields(selectedScrape.data('fields'), response['scrape_fields']);
                    fetchParameters(selectedScrape.data('parameters'), response['scrape_parameters']);
                }
                $('.scrape_fields').each(function(){
                    if (response['scrape_fields'].includes($(this).val())){
                        $(this).prop('checked', true);
                    }
                    $(this).attr('disabled', true);
                });
            // var selectedOption = $(this).find('option:selected');
            // var fields = selectedOption.data('fields');
            // var parameters = selectedOption.data('parameters');
            // fetchFields(fields);
            // fetchParameters(parameters);
        // }
                

            },
            error: function (xhr, status, error) {
                alert("Error: " + error)
            }
        });
    });
});

$('#createNewButton').on('click', function (e) {
    e.preventDefault();
    $('#formInModal').attr('action', mainApi);
    $('#formInModal').attr('method', 'post');
    $('#formInModal')[0].reset();
    $('#createButton').text('Create')
    $('#warningMessage').text('').addClass('d-none');
    $('#id_script').remove();
    recipientsArray = [];
    $('#id_recipients_container').empty();
    $('#id_name').removeAttr('disabled');
    $('#id_asset').removeAttr('disabled');
    $('#id_scrape_category').removeAttr('disabled');
    $('#id_scrape_fields').removeAttr('disabled');
    fetchAsset();
    $('.scrape_fields-group').remove();
    $('.scrape_parameters-group').remove();
});