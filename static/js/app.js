const habitForm = document.querySelector('#new_habit_form');

// send AJAX post request when user submits the new habit form
habitForm.addEventListener('submit',(evt)=>{
    evt.preventDefault();

    const formInput = {
        habit_name : document.querySelector('#habit_name').value,
        frequency : document.querySelector('#frequency').value,
        time_period : document.querySelector('#time_period').value,
        start_date : document.querySelector('#start_date').value,
        reminder : document.querySelector('#reminder').value
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
            
            if(habitData.time_period==="daily"){
                document.querySelector('#daily-row').insertAdjacentHTML('afterend', 
            `<tr>
                <th scope="row">${habitData.habit_name}</th>
                <td>0</td>
                <td>0</td>
                <td>0</td>
            </tr>`);
            } else if(habitData.time_period==="weekly"){
                document.querySelector('#weekly-row').insertAdjacentHTML('afterend', 
            `<tr>
                <th scope="row">${habitData.habit_name}</th>
                <td>0</td>
                <td>0</td>
                <td>0</td>
            </tr>`);
            } else if(habitData.time_period==="monthly"){
                document.querySelector('#monthly-row').insertAdjacentHTML('afterend', 
            `<tr>
                <th scope="row">${habitData.habit_name}</th>
                <td>0</td>
                <td>0</td>
                <td>0</td>
            </tr>`);
            }
            

            // add new habit in the select menu for record
            document.querySelector('#log-habit').insertAdjacentHTML('beforeend',
            `<option value="${habitData.habit_id}">${habitData.habit_name}</option>`
            )
        })
})

// for tooltip when mouse hovers over badges
let tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
let tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
  return new bootstrap.Tooltip(tooltipTriggerEl)
})

// set max day of input date in record form to today
let logDate = document.querySelector('#log-date')
logDate.max = new Date().toLocaleDateString('en-ca')

