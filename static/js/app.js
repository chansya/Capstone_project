'use strict';

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
        
        let habit_recs = Object.entries(responseJson['habits'])
        let color_dict = responseJson['colors']

        // create an array of objects with habit name as key and list of records as value
        let dataArr = [];
        for(const [habit_name, daily_records] of habit_recs){

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

        for(let i=0; i<dataArr.length; i++){
            let name = Object.keys(dataArr[i])[0]
            let data = dataArr[i][name]
            dataSet.push({
                label: name,
                backgroundColor: color_dict[name],
                borderColor: color_dict[name],
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


// load toast message and fetch quotes from API call upon page load
window.onload = (event) => {
    let myAlert = document.querySelectorAll('.toast')[0];
    if (myAlert) {
      let bsAlert = new bootstrap.Toast(myAlert);
      bsAlert.show();
    }
    fetch('/api/quotes')
    .then((response) => response.json())
    .then((quoteData) => {
        let quote= quoteData['quote'];
        let author = quoteData['author'];
        document.querySelector('#quote')
                .textContent = `'${quote}' - ${author}`;
    })
  };

