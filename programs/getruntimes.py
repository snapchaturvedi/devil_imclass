#======================================================================================
# Version 7
# Date: 07APR2024
# Comments: 
### Evaluate time taken for inference of all PTQ models (including time taken to click pictures)
#======================================================================================

# Load libraries
import os
import time
import gpiozero
import numpy as np
import tflite_runtime.interpreter as tflite
import picamera
import gc
 
# Paths
program_path = os.path.join(os.getcwd(), "devil_imclass", "programs")
model_path = os.path.join(program_path, "..", "models")
save_path = os.path.join(program_path, "..", "save")
log_path = os.path.join(program_path, "..", "log")

# Camera variables
n_photos = 10
channels = 3
resolution = [224, 224]
frame_rate = 50
rotate = 180

# Get all model names in path
model_names = os.listdir(model_path)
model_names.sort()

# Initialise list to save all times
times = []

for model_name in model_names:
	print(model_name)
	iteration = 0	
	
	# Load tflite model
	with open(os.path.join(model_path, model_name), 'rb') as fid:
		tflite_model = fid.read()

	# Load interpreter
	interpreter = tflite.Interpreter(model_content=tflite_model)
	interpreter.allocate_tensors()
	in_details = interpreter.get_input_details()
	out_details = interpreter.get_output_details()

	model_inshape = [n_photos] + resolution + [channels] # 10 bursts of resolution*resolution -> 3 channels
	model_outshape = [n_photos + 1] # 10 probabilities each of 10 bursts

	# Resize input and output tensors (batch_size axis) based on how many images you'll feed at once (by default it's 1, let's leave it that way for now)
	# Might want to change it to 10 later if we decide to click 10 images in a burst and feed them all as a batch
	interpreter.resize_tensor_input(in_details[0]["index"], model_inshape)
	interpreter.resize_tensor_input(out_details[0]["index"], model_outshape)
	interpreter.allocate_tensors()
	# This `interpreter` object will be called later to perform inference	

	# Camera tasks
	while iteration < 10:
		# To calculate time taken
		start = time.time()	

		# Click pictures
		with picamera.PiCamera() as camera:
			camera.resolution = resolution
			camera.rotation = rotate
			camera.framerate = frame_rate
			click = np.empty((resolution[0]*resolution[1]*channels), dtype=np.uint8) # 1D array to capture 1 photo at a time
			
			photos = np.array([]) # Initialise empty array to store all the captured photos
			
			while np.shape(photos)[0] < n_photos*resolution[0]*resolution[1]*channels:
				camera.capture(click, "rgb")
				photos = np.append(photos, click)
				
		x = photos.reshape(model_inshape)
		x = x.astype("float32")

		# Inference
		interpreter.set_tensor(in_details[0]["index"], x)
		interpreter.invoke()
		pred = interpreter.get_tensor(out_details[0]["index"])
		print(pred)
		
		# Time taken
		times.append(time.time()-start)
		
		iteration += 1
		print(iteration)
	
	# Delete tflite and interpreter to free memory
	del tflite_model
	del interpreter
	gc.collect()	

# Export times to a csv file
import csv
with open("PChaturvedi_model_runtime.csv", "w") as f:
	write = csv.writer(f)
	for i, name in enumerate(model_names):
		write.writerow([name, times[i*10:(i+1)*10]])
