from collections import Counter
from itertools import chain

import torch
import torchvision.transforms as transforms

from torch.nn import DataParallel
from torch.autograd import Variable

from .model import Net
from .image import Net as ImageNet

with open('app/vocab.json') as f:
    from json import load
    vocab = load(f)

token_to_index = vocab['question']

log = torch.load('weights.pth', map_location='cpu')
num_tokens = len(log['vocab']['question']) + 1

net = DataParallel(Net(num_tokens))
net.load_state_dict(log['weights'])

transform = transforms.Compose((
    transforms.Resize(int(448/0.875)),
    transforms.CenterCrop(448),
    transforms.ToTensor(),
    transforms.Normalize(mean=(0.485, 0.455, 0.406), std=(0.229, 0.224, 0.225)),
))

imagenet = ImageNet()


def vqa(image, question):
    question = question.lower()[:-1].split(' ')
    q_len = len(question)
    vec = torch.zeros(num_tokens).long()
    for i, tok in enumerate(question):
        vec[i] = token_to_index.get(tok, 0)

    q = Variable(vec)
    q_len = Variable(torch.empty(q_len))
    v = Variable(transform(image).unsqueeze_(0).cpu())

    v_net = imagenet(v)
    features = v_net.data.cpu().numpy().astype('float16')

    output = net(features, q, q_len)

    return output
