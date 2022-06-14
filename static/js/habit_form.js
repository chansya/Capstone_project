const newHabitBtn = document.querySelector('#add_habit');
const habitForm = document.querySelector('#habit_form');
const cancelBtn = document.querySelector('#cancel_form');

// display the new habit form when user clicks on "Add a habit" btn
newHabitBtn.addEventListener('click', ()=>{
    habitForm.style.display = 'block';
})
// hide the form when user clicks cancel
cancelBtn.addEventListener('click', ()=>{
    habitForm.style.display = 'none';
})
