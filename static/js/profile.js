const editHabits = document.querySelector('#edit-habits');

editHabits.addEventListener('click', ()=>{
    
    if(editHabits.innerHTML === '<i class="bi bi-pencil-square"></i>'){
        editHabits.innerHTML = '<i class="bi bi-check2-square"></i>';
        const deleteIcons=document.querySelectorAll('.rm-habit');
        for(const icon of deleteIcons){
            icon.style.display = 'inline-block';}
    } else if (editHabits.innerHTML === '<i class="bi bi-check2-square"></i>'){
        editHabits.innerHTML = '<i class="bi bi-pencil-square"></i>';
        const deleteIcons=document.querySelectorAll('.rm-habit');
        for(const icon of deleteIcons){
            icon.style.display = 'none';}
    }
})

const habits = document.querySelectorAll('.habit-item');

for(const habit of habits){
    habit.addEventListener('click', ()=>{
        const habit_id = habit.id;
        let confirmRemove = confirm("Are you sure about removing this habit? All records will be removed too.")
        if (confirmRemove) {
        fetch(`/remove_habit/${habit_id}`)
            .then((res)=>res.json())
            .then((resJson)=>{
                if(resJson.status === 'success'){
                    habit.remove();
                }
                else{
                    console.log("Fail")
                }
            })
        }
    }
    )
}