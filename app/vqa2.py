import config
import data
import utils
import model
import torch
from torch.autograd import Variable
from PIL import Image
import json
imageNet = __import__("preprocess-images")
extract_vocab = __import__("preprocess-vocab")

# input the trained weight
fpath = ""
fname = "/Users/ruochenzhang/Dropbox/Term8/AI/weight.pth"

def our_net(num_tokens):
	# -----input model------
	# structure is in pytorch-vqa.model
    net = torch.nn.DataParallel(model.Net(num_tokens))
    net.load_state_dict(log['weights'])
    return net

def coco_image_loader(ipath):
    transform = utils.get_transform(config.image_size, config.central_fraction)
    img = Image.open(ipath).convert('RGB')
    img = transform(img)
    return img


def _encode_question(max_question_length,question):
        """ Turn a question into a vector of indices and a question length """
        vec = torch.zeros(max_question_length).long()
        for i, token in enumerate(question):
            index = token_to_index.get(token, 0)
            vec[i] = index
        return vec, len(question)


def main(imgpath, qn, use_gpu = False):
	'''
	imgpath: path of input image
	qn: a string
	'''
	# --- load vocab
	with open("vocab.json", 'r') as fd:
    		vocab_json = json.load(fd)
        
	vocab = vocab_json
	token_to_index = vocab['question']

	# --- prepare image (V)
	imagenet = imageNet.Net()
 	# process image
    img_loader = coco_image_loader(imgpath)
    if use_gpu:
    	v = Variable(img_loader.cuda(async=True), volatile=True)
    else:
	    v = Variable(img_loader.cpu(), volatile=True)


	# --- prepare vocab (Q)
	""" Tokenize and normalize questions from a given question json in the usual VQA format. """ vocab (Q)
	question = qn
    question_vocab = question.lower()[:-1]
    question_vocab = question_vocab.split(' ')
    question_vocab = extract_vocab.extract_vocab(question_vocab, start=1)

    log = torch.load(fname,map_location='cpu')
    num_tokens = len(log['vocab']['question']) + 1

    question = _encode_question(num_tokens, question_vocab)
    if use_gpu:
	    q = Variable(question[0].cuda(async=True), volatile=True)
	else:
		q = Variable(question[0], volatile=True)

    # --- prepare q_length for 
    if use_gpu:
	    q_len = Variable(torch.Tensor(question[1]).cuda(async=True), volatile=True)
	else:
		q_len = Variable(torch.Tensor(question[1]), volatile=True)

    # --- generate output
    OurNet = our_net(num_tokens)
#     print(OurNet)
    out = OurNet(v, q, q_len)
    print(out)
    return out


if __name__ == "__main__":
	main('/Users/ruochenzhang/Desktop/1.png',"what is this?")
