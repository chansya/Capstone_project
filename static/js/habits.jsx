'use strict';


function Habits(){

    // useState hook to set habits to empty array as initial value
    const [habits, setHabits] = React.useState([])
    const [records, setRecords] = React.useState([])

    // fetch data from backend then update habits using setHabits
    React.useEffect(()=>{
        fetch('/habits.json')
            .then((response)=>response.json())
            .then((result)=>{
                console.log(result);
                setHabits(result.habits)}
                );
    },[]);

    // populate habit elements from habit list fetched
    const habitEls = habits.map((habit)=>(
        <li key={habit.habit_id}>{habit.habit_name}
        <button className="btn btn-light" onClick={()=>updateRecords(habit.habit_id)}>Check records</button>
        <button className="btn btn-light" onClick={()=>removeHabit(habit.habit_id)}> 
        <img src="static/img/trash.svg" alt="trash">
        </img></button>
        </li>))
    
    // remove habit when trash button is clicked
    function removeHabit(id){
        let confirmRemove = confirm("Are you sure about removing this habit? All records will be removed too.")
        if (confirmRemove) {
            fetch(`/react/remove_habit/${id}`)
            .then((response)=>response.json())
            .then((result) => {
                if(result.status === 'success'){
                    // setting habit list to filtered list
                    const newList = habits.filter((habit)=>habit.habit_id!==id);
                    setHabits(newList)
                }
            });
        };
    }
    

    // fetch record data when habit is selected
    function updateRecords(id){
        console.log(`/react/${id}/records`)
        fetch(`/react/${id}/records`)
            .then((response)=>response.json())
            .then((result)=>{
                console.log(result);
                setRecords(result.records);}
                );
    }
    console.log("HABIT Records!")
    console.log(records)

    function removeRecord(id){
        let confirmRemove = confirm("Are you sure about removing this record?")
        if (confirmRemove) {
            fetch(`/react/remove_record/${id}`)
            .then((response)=>response.json())
            .then((result) => {
                if(result.status === 'success'){
                    // setting habit list to filtered list
                    const newList = records.filter((record)=>record.record_id!==id);
                    setRecords(newList);
                }
            });
        };
    }
   
    // loop thru the records state and create record component
    const recordList = []

    for (const record of records){
        recordList.push(
            <Record
            key = {record.record_id}
            record_date = {record.record_date}
            notes = {record.notes}
            img_url = {record.img_url}
            />,
            <button className="btn btn-light" onClick={()=>removeRecord(record.record_id)}> 
            <img src="static/img/trash.svg" alt="trash">
            </img></button>
        )
    }

    return (
        <React.Fragment>
            
            <div className="sidenav">
                <h2>Habit List: </h2>  
                <ul>{habitEls}</ul>
            </div>

            <div className="main">
                <h2>Record List:</h2>
                <ul>{recordList}</ul>
            </div>
            
        </React.Fragment>
        );
}

// Single record component
function Record(props){
    return (
        <li>
            <p>Recorded on {props.record_date}</p>
            <p>Notes: {props.notes}</p>
            <img src="props.img_url" alt="record_image" />
            
        </li>
    );
}
   


ReactDOM.render(
    <Habits />, 
    document.querySelector('#root'));