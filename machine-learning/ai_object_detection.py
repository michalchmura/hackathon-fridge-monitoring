# USAGE
# python deep_learning_object_detection.py --image images/example_01.jpg \
#	--prototxt MobileNetSSD_deploy.prototxt.txt --model MobileNetSSD_deploy.caffemodel

# import the necessary packages
import numpy as np
import argparse
import cv2
import time
import json

# Define class for our Result return object
class Result:
	labels = []
	def labelsToJSON(self):
		return json.dumps(self.labels, default=lambda o: o.__dict__, 
				sort_keys=True, indent=4)
	def toJSON(self):
		return json.dumps(self, self.labels, default=lambda o: o.__dict__, 
				sort_keys=True, indent=4)
	

# Initialize result object
result = Result()

class Label:
	label = ""
	confidence = ""
	def __init__(self, label, confidence):
		self.label = label
		self.confidence = confidence
	def display(self):
		print('Label: ' + self.label)
		print('Confidence: ', self.confidence)
	def toJSON(self):
		return json.dumps(self, default=lambda o: o.__dict__, 
				sort_keys=True, indent=4)

# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image", required=True,
	help="path to input image")
ap.add_argument("-p", "--prototxt", required=True,
	help="path to Caffe 'deploy' prototxt file")
ap.add_argument("-m", "--model", required=True,
	help="path to Caffe pre-trained model")
ap.add_argument("-c", "--confidence", type=float, default=0.2,
	help="minimum probability to filter weak detections")
args = vars(ap.parse_args())

# initialize the list of class labels MobileNet SSD was trained to
# detect, then generate a set of bounding box colors for each class
CLASSES = ["background", "aeroplane", "bicycle", "bird", "boat",
	"bottle", "bus", "car", "cat", "chair", "cow", "diningtable",
	"dog", "horse", "motorbike", "person", "pottedplant", "sheep",
	"sofa", "train", "tvmonitor"]
COLORS = np.random.uniform(0, 255, size=(len(CLASSES), 3))

# load our serialized model from disk
# print("[INFO] loading model...")
net = cv2.dnn.readNetFromCaffe(args["prototxt"], args["model"])

# load the input image and construct an input blob for the image
# by resizing to a fixed 300x300 pixels and then normalizing it
# (note: normalization is done via the authors of the MobileNet SSD
# implementation)
image = cv2.imread(args["image"])
(h, w) = image.shape[:2]
blob = cv2.dnn.blobFromImage(cv2.resize(image, (300, 300)), 0.007843, (300, 300), 127.5)

# pass the blob through the network and obtain the detections and
# predictions
# print("[INFO] computing object detections...")
net.setInput(blob)
detections = net.forward()

# loop over the detections
for i in np.arange(0, detections.shape[2]):
	# extract the confidence (i.e., probability) associated with the
	# prediction
	confidence = detections[0, 0, i, 2]

	# filter out weak detections by ensuring the `confidence` is
	# greater than the minimum confidence
	if confidence > args["confidence"]:
		# extract the index of the class label from the `detections`,
		# then compute the (x, y)-coordinates of the bounding box for
		# the object
		idx = int(detections[0, 0, i, 1])
		box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
		(startX, startY, endX, endY) = box.astype("int")

		# Create the label object
		labelObj = Label(CLASSES[idx], "{:.5f}".format(confidence))
		# Add the Labels to the result array
		result.labels.append(labelObj)

		label = "{}: {:.2f}%".format(CLASSES[idx], confidence * 100)
		# print("[INFO] {}".format(label))
		cv2.rectangle(image, (startX, startY), (endX, endY),
			COLORS[idx], 2)
		y = startY - 15 if startY - 15 > 15 else startY + 15
		cv2.putText(image, label, (startX, y),
			cv2.FONT_HERSHEY_SIMPLEX, 0.5, COLORS[idx], 2)

# Set current time as variable
current_time = time.strftime("%Y-%m-%d_%H-%M-%S")
outputFilePath = "./output/" + current_time + ".jpg"

# Save output file with date time format
cv2.imwrite(outputFilePath, image)

# show the output image
# cv2.imshow("Output", image)
jsonStructure="""
{
	\"info\": {
		\"input\": \"""" + args["image"] + """\",
		\"output\": \"output/""" + current_time + """.jpg\"
	},
	\"results\":
		""" + result.labelsToJSON() + """
}
"""

parsed = json.loads(jsonStructure)
print(json.dumps(parsed, indent=4, sort_keys=True))
# print(jsonStructure)

cv2.waitKey(0)