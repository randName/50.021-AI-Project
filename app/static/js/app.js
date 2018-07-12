const reader = new FileReader();

class VQA {
  constructor() {
    this.image = null;
    this.question = null;
  }

  setQuestion(e) {
    this.question = e.value;
  }

  setImage(e) {
    reader.onloadend = () => {this.image = reader.result};
    reader.readAsDataURL(e.files[0]);
  }

  query() {
    let image = this.image;
    let question = this.question;

    if (!image) {
      return Promise.resolve({status: 'error', message: 'no image'})
    }

    if (!question) {
      return Promise.resolve({status: 'error', message: 'no question'})
    }

    return fetch('/', {
      method: 'POST', mode: 'cors',
      body: JSON.stringify({image, question}),
      headers: {'content-type': 'application/json'}
    }).then(r => r.json())
  }
}

let vqa = new VQA();
