from io import BytesIO
from base64 import b64decode

from PIL import Image
from flask import Flask, json, request

from .vqa import vqa

app = Flask(__name__)


class APIError(Exception):
    pass


@app.errorhandler(APIError)
def api_error(e):
    return json.jsonify({'status': 'error', 'message': str(e)})


@app.route('/', methods=('GET', 'POST'))
def index():
    if request.method == 'GET':
        return app.send_static_file('index.html')

    q = request.get_json()

    try:
        image = q['image']
        fmt, data = image[4:].split(';base64,')
        image = Image.open(BytesIO(b64decode(data.encode())))
    except KeyError:
        raise APIError('no image received')
    except ValueError:
        raise APIError('malformed data')
    except OSError:
        raise APIError('cannot identify image')

    try:
        question = q['question']
    except KeyError:
        raise APIError('no question asked')

    answer = vqa(image, question)

    resp = {
        'status': 'ok',
        'answer': answer,
    }

    return json.jsonify(resp)
