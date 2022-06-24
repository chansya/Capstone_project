'use strict';

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
            // let prompt = document.querySelector('#new_habit_prompt');
            // if(prompt){prompt.remove();}
            
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


// make multiple lines in one chart
fetch('/daily_habit.json')
    .then((response) => response.json())
    .then((responseJson) => {
    // console.log('JSON response:')
    // console.log(responseJson)
        let dataArr = []
        for(const [habit_id, daily_records] of Object.entries(responseJson)){
            // console.log(habit_id)
            // console.log(daily_records)
            
            const data = daily_records.map((dailyTotal) => ({
                x: dailyTotal.date,
                y: dailyTotal.times_done,
                }));
            // console.log(data)
            dataArr.push(data)}
        console.log("List of Data Arrays")
        console.log(dataArr)

        let dataSet=[]
        for(let i=0; i<dataArr.length; i++){
            dataSet.push({
                label: `Habit${i+1}`,
                // backgroundColor: getRandomColor(),
                borderColor: getRandomColor(),
                data: dataArr[i]
            })
            console.log("Inside for loop")
            console.log(dataArr[i])
        }
        console.log(dataSet)

            
        new Chart(document.querySelector('#multi-line'), {
        type: 'line',
        data: {
            datasets: dataSet,
        },
        options: {
            scales: {
            x: {
                type: 'time',
                time: {
                
                tooltipFormat: 'LLLL dd', // Luxon format string
                unit: 'day',
                },
            },
            },
        },
        });
        }

    );

function getRandomColor(){
    const randomBetween = (min, max) => min + Math.floor(Math.random() * (max - min + 1));
    const r = randomBetween(0, 255);
    const g = randomBetween(0, 255);
    const b = randomBetween(0, 255);
    const rgb = `rgb(${r},${g},${b})`;
    return rgb;
}
// confetti
// var myCanvas = document.createElement('canvas');
// document.body.appendChild(myCanvas);

// var myConfetti = confetti.create(myCanvas, {
//   resize: true,
//   useWorker: true
// });
// myConfetti({
//   particleCount: 150,
//   spread: 180
//   // any other options from the global
//   // confetti function
// });
// confetti();