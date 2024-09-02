import torch
import torchvision.transforms as transforms
from lenet import LeNet
from PIL import Image


def image_classification(file):
    model = LeNet()
    ckpt = torch.load('lenet.pth')
    model.load_state_dict(ckpt['state_dict'])

    model.eval()

    image = Image.open(file)

    transform = transforms.Compose([
        transforms.Resize((28, 28)),
        transforms.Grayscale(num_output_channels=1),
        transforms.ToTensor()
    ])

    image_array = transform(image)
    image_array = image_array.unsqueeze(0)
    print(image_array.shape)

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model.to(device)
    image_array = image_array.to(device)
    output = model(image_array)
    _, result = torch.max(output, dim=1)

    return f'Classification result: {result.item()}'
