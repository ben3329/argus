$(document).ready(function () {
    const accessTypeSelect = $('#id_access_type');
    const IdField = $('#id_username').parent();
    const PasswordField = $('#id_password').parent();
    const secretField = $('#id_secret').parent();

    function updateFormFields() {
        if (accessTypeSelect.val() === 'ssh_password') {
            IdField.closest('.row').show();
            PasswordField.closest('.row').show();
            secretField.closest('.row').hide();
            IdField.prop('required', true);
            PasswordField.prop('required', true);
            secretField.prop('required', false);
        } else if (accessTypeSelect.val() === 'ssh_private_key') {
            IdField.closest('.row').hide();
            PasswordField.closest('.row').hide();
            secretField.closest('.row').show();
            IdField.prop('required', false);
            PasswordField.prop('required', false);
            secretField.prop('required', true);
        }
    }

    accessTypeSelect.on('change', updateFormFields);
    updateFormFields();  // Call the function initially to set the correct fields visibility
});