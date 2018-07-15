const reader = new FileReader();
const filename = document.getElementById('fn');
const snackbar = document.getElementById('sn');
const answertx = document.getElementById('an');
const uploadbt = document.getElementById('bn');
const spinner = document.getElementById('spin');

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
    if (!file.type.includes('image')) {
      snack('not an image');
      return;
    }
    filename.value = file.name;
    reader.onloadend = () => {this.image = reader.result};
    reader.readAsDataURL(file);
  }

  ask() {
    spinner.MaterialSpinner.start();
    this.query().then(r => {
      if (r.status == 'ok') {
        console.log(r);
        an.MaterialTextfield.input_.value = r.answer;
        an.MaterialTextfield.checkDirty();
      } else {
        snack(r.message);
      }
      spinner.MaterialSpinner.stop();
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
    }).then(r => r.json())
      .catch(e => Promise.resolve({status: 'error', message: 'server error'}));
  }
}

const vqa = new VQA();
