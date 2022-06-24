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


// make AJAX to get habit data, then create chart with multiple datasets
fetch('/chart_data.json')
    .then((response) => response.json())
    .then((responseJson) => {
        // create an array of objects with habit name as key and list of records as value
        let dataArr = []
        for(const [habit_name, daily_records] of Object.entries(responseJson)){

            const data = daily_records.map((dailyTotal) => ({
                x: dailyTotal.date,
                y: dailyTotal.times_done,
                }));

            let data_dict = {}
            data_dict[habit_name] = data
            dataArr.push(data_dict);
        }
        // create array of datasets 
        let dataSet=[]
        let colors = ['#FFCFD2','#98F5E1','#B9FBC0','#FDE4CF',
        '#CFBAF0','#F1C0E8','#90DBF4','#FBF8CC','#A3C4F3','#8EECF5']

        for(let i=0; i<dataArr.length; i++){
            let name = Object.keys(dataArr[i])[0]
            let data = dataArr[i][name]
            dataSet.push({
                label: name,
                backgroundColor: colors[i],
                borderColor: colors[i],
                data: data
            })
        }

        // create and configure chart 
        new Chart(document.querySelector('#multi-line'), {
        type: 'bar',
        data: {
            datasets: dataSet,
        },
        options: {
            responsive: true,
            scales: {
            x: {
                title:{
                    display: true,
                    text: "Date"
                },
                type: 'time',
                time: {
                
                tooltipFormat: 'LLLL dd', // Luxon format string
                unit: 'week',
                },
            },
            y: {
                title: {
                  display: true,
                  text: 'Times Done'
                },
                min: 0,
                suggestedMax: 3,
                ticks: {
                  stepSize: 1
                }
              }
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