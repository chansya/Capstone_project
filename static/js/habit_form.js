const newHabitBtn = document.querySelector('#show_form');
const habitForm = document.querySelector('#habit_form');
const cancelBtn = document.querySelector('#cancel_form');
const saveBtn = document.querySelector('#save_form');

// display the new habit form when user clicks on "Add a habit" btn
newHabitBtn.addEventListener('click', ()=>{
    habitForm.style.display = 'block';
})

// hide the form when user clicks "Cancel" btn
cancelBtn.addEventListener('click', ()=>{
    habitForm.style.display = 'none';
})

// send AJAX post request when user submits the new habit form
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
        .then(habitData=>{
            let prompt = document.querySelector('#new_habit_prompt');
            if(prompt){prompt.remove();}
           
            document.querySelector('#habit_list').insertAdjacentHTML('beforeend', 
            `<p>${habitData.habit_name} (${habitData.frequency} times ${habitData.time_period})</p>
            <p>Current streak: ${habitData.current_streak}</p>
            <p>Longest streak: ${habitData.max_streak}</p>
            <hr>`);

            document.querySelector('#habit_done').insertAdjacentHTML('beforeend',
            `<option value="${habitData.habit_name}">${habitData.habit_name}</option>`
            )
        })
})


// select the list forms
// const recordForms = document.querySelectorAll('.record_form');

// for(const recordForm of recordForms){
//     recordForm.addEventListener('submit',(evt)=>{
//         const form = evt.target;
//         evt.preventDefault();

//         const formInput = {
//             habit_id : form.id,
//             finished : document.querySelector('#finished').value,
//             notes : document.querySelector('#notes').value,
//             record_date : document.querySelector('#record_date').value
//         }
    
//         fetch('/create_record', {
//             method: 'POST',
//             body: JSON.stringify(formInput),
//             headers:{
//                 'Content-Type' : 'application/json',
//             },
//         })
//             .then(response => response.json())
//             .then(responseJson=>{
//                 alert(responseJson.status);
//             })
//     })
// }


// for rendering calendar
document.addEventListener('DOMContentLoaded', function() {
    let calendarEl = document.getElementById('calendar');
    let calendar = new FullCalendar.Calendar(calendarEl, {
      initialView: 'dayGridMonth'
    });
    calendar.render();
  });