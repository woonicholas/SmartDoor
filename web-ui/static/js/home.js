
function songSelect(event){
  console.log(event.target.id)
  var formData = new FormData(document.querySelector("form"));
  console.log(formData.get(`songName${event.target.id}`));
  axios({
    method: 'put',
    url: 'http://127.0.0.1:5000/select-song',
    data: {
      id: event.target.id,
      song: formData.get(`songName${event.target.id}`)
    }
  }).then(response => {
    document.getElementById(`song-select ${event.target.id}`).innerHTML = formData.get(`songName${event.target.id}`);
  });
}

function createUser(event){
  event.preventDefault()
  var formData = new FormData(document.querySelector("form"));
  axios({
    method: 'post',
    url: 'http://127.0.0.1:5000/create_user',
    data: {
      name: formData.get('personName'),
      song: formData.get('songName')
    }
  }).then(response =>{
    location.reload();
  })
}

function handleNameClick(event){
  location.href = `http://127.0.0.1:5000/employee/${event.target.id}`;
}