
function songSelect(event){
  console.log(event.target.id);
  axios({
    method: 'put',
    url: 'http://127.0.0.1:5000/select-song',
    data: {
      id: event.target.id,
      song: event.target.text
    }
  }).then(response => {
    document.getElementById('song-select').innerHTML = event.target.text;
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
    console.log('yessir');
    location.reload();
  })
}