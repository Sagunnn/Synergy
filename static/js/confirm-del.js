document.addEventListener('DOMContentLoaded', function () {
  
  const deleteForms = document.querySelectorAll('.delete-department');
  deleteForms.forEach(function(form) {
    form.addEventListener('submit', function(event) {
      event.preventDefault();
      const confirmed = confirm('Do you want to delete this item?');
      if (confirmed) {
        // Create a hidden input field to indicate that the form was submitted
        const submitInput = document.createElement('input');
        submitInput.type = 'hidden';
        submitInput.name = 'Delete';
        submitInput.value = 'true';
        form.appendChild(submitInput);

        // Submit the form
        form.submit();
        console.log('Submit')
      }
    });
  });
});