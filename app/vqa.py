import torch

from torchvision import transforms
from torch.autograd import Variable
from torch.nn import DataParallel, Softmax

from . import config
from .model import Net, Resnet

with open(config.vocabulary_path) as f:
    from json import load
    vocab = load(f)

results = torch.load(config.results_path, map_location=lambda s, l: s)
answers = {v: k for k, v in vocab['answer'].items()}
tok_to_idx = vocab['question']

softmax = Softmax(dim=1)
resnet = Resnet()
resnet.eval()

net = DataParallel(Net(len(tok_to_idx) + 1))
net.load_state_dict(results['weights'])
net.eval()

transform = transforms.Compose((
    transforms.Resize(int(config.image_size / config.central_fraction)),
    transforms.CenterCrop(config.image_size),
    transforms.ToTensor(),
    transforms.Normalize(mean=(0.485, 0.456, 0.406), std=(0.229, 0.224, 0.225))
))


def vqa(image, question, top_k=5):
    img = transform(image)

    qn = question.lower().replace('?', '').split(' ')
    q_len = len(qn)
    vec = torch.zeros(q_len).long()
    for i, tok in enumerate(qn):
        vec[i] = tok_to_idx.get(tok, 0)

    with torch.no_grad():
        q = Variable(vec.unsqueeze(0))
        q_len = Variable(torch.tensor((q_len,)))
        v = Variable(resnet(img.unsqueeze(0)))

        output = softmax(net(v, q, q_len))
        answer = output.data.topk(top_k, dim=1)
        for i in range(top_k):
            yield answers[int(answer[1][0][i])], float(answer[0][0][i])
