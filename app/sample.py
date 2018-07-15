import sys
import os.path
import math
import json

import torch.nn as nn
import torch.utils.data
import torch
import torchvision.models as models
from torch.autograd import Variable

from . import config, data, utils, model
from .resnet import resnet as caffe_resnet


class Sample():
    def __init__(self, path):
        with open(config.vocabulary_path, 'r') as fd:
            vocab = json.load(fd)
        results = torch.load(path, map_location=lambda storage, loc: storage)

        self.answers = {v: k for k, v in vocab['answer'].items()}
        self.token_to_index = vocab['question']

        self.resnet = Net()
        self.net = nn.DataParallel(model.Net(len(vocab['question']) + 1))

        self.net.load_state_dict(results['weights'])
        self.softmax = nn.Softmax(dim=1)

        self.net.eval()
        self.resnet.eval()


    def encode_question(self, question):
        """ Turn a question into a vector of indices and a question length """
        vec = torch.zeros(len(question)).long()
        for i, token in enumerate(question):
            index = self.token_to_index.get(token, 0)
            vec[i] = index
        return vec, len(question)


    def sample(self, image, question, topk = 5):
        """ Processes a question and image, passes it through the trained net and returns an answer """
        question = question.lower().replace("?", "")
        question = question.split(' ')
        q, q_len = self.encode_question(question)

        transform = utils.get_transform(config.image_size, config.central_fraction)
        inputImg = transform(image)

        with torch.no_grad():
            q = Variable(q.unsqueeze(0))
            q_len = Variable(torch.tensor([q_len]))
            v = Variable(self.resnet(inputImg.unsqueeze(0)))

            out = self.net(v, q, q_len)

            out = self.softmax(out) # to get confidence

            answer = out.data.topk(topk, dim=1)

            answers = []

            for i in range(topk):
                answers.append((self.answers[int(answer[1][0][i])], float(answer[0][0][i])))

        return answers


class Net(nn.Module):
    def __init__(self):
        super(Net, self).__init__()
        self.model = caffe_resnet.resnet152(pretrained=True)

        def save_output(module, input, output):
            self.buffer = output
        self.model.layer4.register_forward_hook(save_output)

    def forward(self, x):
        self.model(x)
        return self.buffer

