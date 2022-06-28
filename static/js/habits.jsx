'use strict';

// function Habit(props){
//     return (
//         <p>{props.name}</p>
//     );
// }
function Habits(){

    // use the useState hook to set cards to empty array as initial value, 
    // then when data is fetched, update habits using setHabits
    const [habits, setHabits] = React.useState([])
    
    React.useEffect(()=>{
        fetch('/habits.json')
            .then((response)=>response.json())
            .then((result)=>{
                console.log(result);
                setHabits(result.habits)}
                );
    },[]);
    
    // remove habit when button is clicked by setting habit list to filtered list
    function handleRemove(id){
        let confirmRemove = confirm("Are you sure about removing this habit? All records will be removed too.")
        console.log(confirmRemove)
        if (confirmRemove) {
            fetch(`/api/remove/${id}`)
            .then((response)=>response.json())
            .then((result) => {
                setHabits(result.habits)
            });
        };
    }

    const habitList = [];
    for (const habit of habits){
        habitList.push(
        <li key={habit.habit_id}>{habit.habit_name}
        <button type="button" onClick={()=>handleRemove(habit.habit_id)}>
            Remove
        </button>
        </li>);
    }
    return (
        <React.Fragment>
            <h2>Habit List: </h2>
            
            <ul>{habitList}</ul>

            
        </React.Fragment>
        
        );
}

function RecordList(){
    const [records, setRecords] = React.useState([])
    React.useEffect(()=>{
        // how to get records of specific habit??
        fetch('/records.json')
            .then((response)=>response.json())
            .then((result)=>{
                console.log(result);
                setRecords(result.records)}
                );
    },[]);
}


ReactDOM.render(
    <Habits />, 
    document.querySelector('#root'));