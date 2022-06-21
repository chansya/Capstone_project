const newHabitBtn = document.querySelector('#show_form');
const habitForm = document.querySelector('#new_habit_form');
const cancelBtn = document.querySelector('#cancel_form');
const saveBtn = document.querySelector('#save_form');
const recordForm = document.querySelector('#record_form');

// display the new habit form when user clicks on "Add a habit" btn
// newHabitBtn.addEventListener('click', ()=>{
//     habitForm.style.display = 'block';
// })

// hide the form when user clicks "Cancel" btn
// cancelBtn.addEventListener('click', ()=>{
//     habitForm.style.display = 'none';
// })

// send AJAX post request when user submits the new habit form
habitForm.addEventListener('submit',(evt)=>{
    evt.preventDefault();

    const formInput = {
        habit_name : document.querySelector('#habit_name').value,
        frequency : document.querySelector('#frequency').value,
        time_period : document.querySelector('#time_period').value,
        start_date : document.querySelector('#start_date').value
    }
    console.log(formInput)
    // send AJAX post request to add new record to database
    fetch('/create_habit', {
        method: 'POST',
        body: JSON.stringify(formInput),
        headers:{
            'Content-Type' : 'application/json',
        },
    })
        .then(response => response.json())
        .then(habitData=>{
            let prompt = document.querySelector('#new_habit_prompt');
            if(prompt){prompt.remove();}
        
            // add new habit under My habits
            document.querySelector('#habit_list').insertAdjacentHTML('beforeend', 
            `<p>${habitData.habit_name} (${habitData.frequency} times ${habitData.time_period})</p>
            <p id="curr_for_${habitData.habit_id}">Current streak: ${habitData.current_streak}</p>
            <p id="max_for_${habitData.habit_id}">Longest streak: ${habitData.max_streak}</p>
            <hr>`);

            // add new habit in the select menu for record
            document.querySelector('#modal-habit').insertAdjacentHTML('beforeend',
            `<option value="${habitData.habit_id}">${habitData.habit_name}</option>`
            )
        })
})

var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
  return new bootstrap.Tooltip(tooltipTriggerEl)
})


// document.querySelector("img[data-bs-toggle='tooltip']").tooltip()