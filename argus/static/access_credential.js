$(document).ready(function () {
    const accessTypeSelect = $('#id_access_type');
    const PasswordField = $('#id_password').parent();
    const secretField = $('#id_secret').parent();

    function updateFormFields() {
        if (accessTypeSelect.val() === 'ssh_password') {
            PasswordField.closest('.row').show();
            secretField.closest('.row').hide();
            PasswordField.prop('required', true);
            secretField.prop('required', false);
        } else if (accessTypeSelect.val() === 'ssh_private_key') {
            PasswordField.closest('.row').hide();
            secretField.closest('.row').show();
            PasswordField.prop('required', false);
            secretField.prop('required', true);
        }
    }

    accessTypeSelect.on('change', updateFormFields);
    updateFormFields();  // Call the function initially to set the correct fields visibility
});