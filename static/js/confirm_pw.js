function checkPassword() {
    const password = document.querySelector('#pw');
    const confirm = document.querySelector('#confirm_pw');
    if (confirm.value === password.value) {
      confirm.setCustomValidity('');
    } else {
      confirm.setCustomValidity('Passwords do not match.');
    }
  }

