'use strict';

// send AJAX post request when user submits the new habit form 
const habitForm = document.querySelector('#new_habit_form');
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
        let dataArr = [];
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
        let dataSet=[];
        let colors = ['#c5dedd','#bcd4e6','#fad2e1','#eddcd2','#cddafd',
        '#f0efeb','#dbe7e4','#d6e2e9','#fde2e4','#dfe7fd'];

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
        type: 'line',
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
                unit: 'day',
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

// show chart upon button click


window.onload = (event) => {
    let myAlert = document.querySelectorAll('.toast')[0];
    if (myAlert) {
      let bsAlert = new bootstrap.Toast(myAlert);
      bsAlert.show();
    }
  };