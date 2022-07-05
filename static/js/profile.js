// To remove a habit
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
})


// To change password
const pwBtn =document.querySelector('#pw-btn');
const pwForm = document.querySelector('#change-pw-form');
const cancelBtn = document.querySelector('#cancel-pw');
const saveBtn = document.querySelector('#save-pw');

pwBtn.addEventListener('click', ()=>{
    pwForm.style.display = 'inline-block';
})

cancelBtn.addEventListener('click', ()=>{
    pwForm.style.display = 'none';
})
saveBtn.addEventListener('click', (evt)=>{
    const password = document.querySelector('#new_pw').value;
    console.log(password)
    const confirm = document.querySelector('#cfm_pw').value;
    console.log(confirm)
    evt.preventDefault();
    if(password === confirm){
        const formInput = {
            new_pw: password,
        };
        console.log(formInput)
        fetch('/change_pw', {
            method: 'POST',
            body: JSON.stringify(formInput),
            headers: {
                'Content-Type' : 'application/json',
            },
        })
         .then((res)=>res.json())
         .then((result)=>{
            if (result.status === 'success'){
                console.log('Success!')
                pwForm.style.display = 'none';
                document.querySelector('#pw-btn-li').insertAdjacentHTML('afterend', 
                `<p id="pw-success">Password has been changed.</p>`)
            }
         })
    }
    

})