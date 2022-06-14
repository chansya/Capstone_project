const newHabitBtn = document.querySelector('#show_form');
const habitForm = document.querySelector('#habit_form');
const cancelBtn = document.querySelector('#cancel_form');
const saveBtn = document.querySelector('#save_form');
// display the new habit form when user clicks on "Add a habit" btn
newHabitBtn.addEventListener('click', ()=>{
    habitForm.style.display = 'block';
})
// hide the form when user clicks cancel
cancelBtn.addEventListener('click', ()=>{
    habitForm.style.display = 'none';
})

habitForm.addEventListener('submit',(evt)=>{
    evt.preventDefault();

    const formInput = {
        habit_name : document.querySelector('#habit_name').value,
        frequency : document.querySelector('#frequency').value,
        time_period : document.querySelector('#time_period').value,
        start_date : document.querySelector('#start_date').value
    }

    fetch('/create_habit', {
        method: 'POST',
        body: JSON.stringify(formInput),
        headers:{
            'Content-Type' : 'application/json',
        },
    })
        .then(response => response.json())
        .then(responseJson=>{
            alert(responseJson.status);
            document.querySelector('#habit_list').insertAdjacentHTML('beforeend', 
            `<p>${formInput.habit_name}</p>
            <p>Current streak: 0</p>
            <p>Longest streak: 0</p>
            <span>${formInput.frequency} ${formInput.time_period}</span>
            <button>Done!</button>`);
        })
})