const reader = new FileReader();
const filename = document.getElementById('fn');
const snackbar = document.getElementById('sn');
const answertx = document.getElementById('an');
const uploadbt = document.getElementById('bn');

filename.onclick = () => uploadbt.click();

function snack(message) {
  snackbar.MaterialSnackbar.showSnackbar({message});
}

class VQA {
  constructor() {
    this.image = null;
    this.question = null;
  }

  setQuestion(e) {
    this.question = e.value;
  }

  setImage(e) {
    let file = e.files[0];
    filename.value = file.name;
    reader.onloadend = () => {this.image = reader.result};
    reader.readAsDataURL(file);
  }

  ask() {
    this.query().then(r => {
      if (r.status == 'ok') {
        console.log(r);
        an.MaterialTextfield.input_.value = r.answer;
        an.MaterialTextfield.checkDirty();
      } else {
        snack(r.message);
      }
    });
  }

  query() {
    let image = this.image;
    let question = this.question;

    if (!image) {
      return Promise.resolve({status: 'error', message: 'no image'});
    }

    if (!question) {
      return Promise.resolve({status: 'error', message: 'no question'});
    }

    return fetch('/', {
      method: 'POST', mode: 'cors',
      body: JSON.stringify({image, question}),
      headers: {'content-type': 'application/json'}
    }).then(r => r.json());
  }
}

const vqa = new VQA();
