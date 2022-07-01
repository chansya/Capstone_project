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

    React.useEffect(()=>{
        fetch('/records.json')
            .then((response)=>response.json())
            .then((result)=>{
                console.log(result);
                setRecords(result.records)}
                );
    },[]);

    // populate habit elements from habit list fetched
    const habitEls = habits.map((habit)=>(
        <div key={habit.habit_id}>       
            <button className="btn btn-light" onClick={()=>updateRecords(habit.habit_id)}>{habit.habit_name}</button>
            <button className="btn btn-light" id="remove-habit-btn" onClick={()=>removeHabit(habit.habit_id)}> 
            <img src="static/img/trash.svg" alt="trash">
            </img></button>
        </div>))
    
    // remove habit when trash button is clicked
    function removeHabit(habit_id){
        let confirmRemove = confirm("Are you sure about removing this habit? All records will be removed too.")
        if (confirmRemove) {
            fetch(`/remove_habit/${habit_id}`)
            .then((response)=>response.json())
            .then((result) => {
                if(result.status === 'success'){
                    // setting habit list to filtered list
                    const newList = habits.filter((habit)=>habit.habit_id!==habit_id);
                    setHabits(newList)
                }
            });
        };
    }
    
    // fetch record data when habit is selected
    function updateRecords(habit_id){

        fetch(`/${habit_id}/records`)
            .then((response)=>response.json())
            .then((result)=>{
                setRecords(result.records);}
                );
    }

    // remove record when remove button is clicked
    function removeRecord(rec_id){
        let confirmRemove = confirm("Are you sure about removing this record?")
        if (confirmRemove) {
            fetch(`/remove_record/${rec_id}`)
            .then((response)=>response.json())
            .then((result) => {
                if(result.status === 'success'){
                    // setting habit list to filtered list
                    const newList = records.filter((record)=>record.record_id!==rec_id);
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
            record_id = {record.record_id}
            habit_name = {record.habit_name}
            record_date = {record.record_date}
            notes = {record.notes}
            img_url = {record.img_url}
            removeRecord = {removeRecord}
            />,
            // <button className="btn btn-light" onClick={()=>removeRecord(record.record_id)}> 
            // <img src="static/img/trash.svg" alt="trash">
            // </img></button>
        )
    }
    
    return (
        <React.Fragment>
            {/* TOP section */}
            <section className ="py-5 text-center container">
                <div className ="row py-lg-5">
                    <div className ="col-lg-6 col-md-8 mx-auto">
                        <h1 className ="fw-light">MY RECORDS</h1>
                        <p className ="lead text-muted"></p>
                        {habitEls}
                    </div>
                </div>
            </section>

            {/* RECORD SECTION */}
            <div className="container">
                <div className="row row-cols-1 row-cols-sm-2 row-cols-md-3 g-3">               
                    {recordList}
                </div>
            </div>
        </React.Fragment>
        );
}

// Single record component
function Record(props){
    return (
        <div className="col">
            <div className="card shadow-sm">
                <img src={props.img_url} className="card-img-top" alt="record-image"/>
                <div className="card-body">
                <h6 class="card-title">{props.habit_name}</h6>
                <p className="card-text">{props.notes}</p>
                <div className="d-flex justify-content-between align-items-center">
                    <div className="btn-group">
                    <button type="button" className="btn btn-sm btn-outline-secondary" onClick={() => { props.removeRecord(props.record_id) }}>
                        <small>Remove</small>
                    </button>
                    </div>
                    <small className="text-muted">{props.record_date}</small>
                    </div>
                </div>
            </div>
        </div>
    );
}
   

ReactDOM.render(
    <Habits />, 
    document.querySelector('#root'));