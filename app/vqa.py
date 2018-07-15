from .sample import Sample
s = Sample('weights.pth')


def vqa(image, question):
    output = s.sample(image, question)
    print(output)
    return output[0][0]
