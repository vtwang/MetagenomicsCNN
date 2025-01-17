import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
import torchvision
import torchvision.transforms as transforms
import matplotlib.pyplot as plt
import torch.optim as optim
from cnn import Net
import os

PATH = '../data/images/'
TEST_SIZE = 20
RNN_FILE = './genomics_rnn.pth'
transform = transforms.Compose([transforms.ToTensor()])
onehot_size = 4

files = os.listdir(PATH)
classes = [f.split('.'[0]) for f in files]

# retrieve the data from each file
# except the first 20, load the rest
class TestSet(torch.utils.data.Dataset):
	def __init__(self, filepath, test_size, transform=None):
		self.data = []
		self.transform = transform
		files = os.listdir(filepath)
		for i, f in enumerate(files):
			dat = np.load(filepath + '/' + f)[:test_size]
			for d in dat:
				t = d.reshape(-1, onehot_size)
				self.data.append( (t, i) )

	def __len__(self):
		return len(self.data)
	def __getitem__(self, idx):
		sample, label = self.data[idx]
		if self.transform:
			sample = self.transform(sample)
		return sample, label

testset = TestSet(PATH, TEST_SIZE, transform=transform)
testloader = torch.utils.data.DataLoader(testset, batch_size=4, shuffle=False, num_workers=2)

rnn = RNN()
rnn.load_state_dict(torch.load(RNN_FILE))

# outputs = net(images)
# _, predicted = torch.max(outputs, 1)
# print('Predicted: ', ' '.join('%5s' % classes[predicted[j]] for j in range(4)))

correct = 0
total = 0
with torch.no_grad():
	for data in testloader:
		inputs, labels = data
		hidden = rnn.initHidden()
		for j in range(inputs.size()[0]):
			outputs, hidden = rnn(inputs.float(), hidden)
		_, predicted = torch.max(outputs.data, 1)
		total += labels.size(0)
		correct += (predicted == labels).sum().item()
print('Accuracy of the RNN on the test images: %d %%' % (100 * correct / total))
