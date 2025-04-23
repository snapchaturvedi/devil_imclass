#======================================================================================
# Version 6
# Date: 06JUN2024
# Comments: 
### Evaluate time taken for inference ONLY of all models in devil_imclass/models folder
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

# Get device name
f = os.open("/proc/device-tree/model", os.O_RDONLY)
readBytes = os.read(f, 50)
os.close(f)
devname = readBytes.decode().strip("utf-8").replace(".", "_").replace(" ", "").replace("\0", "")

save_file_name = rf"PChaturvedi_runtimes_{devname}.csv"
print(save_file_name)

# Create save file if does not exist
if save_file_name not in  os.listdir(save_path):
	with open(os.path.join(save_path, save_file_name), "w") as f:
		f.write(f"model, avg_time\n")

# Camera variables
N_PHOTOS = 10
CHANNELS = 3
RESOLUTION = [224, 224]
FRAME_RATE = 50
ROTATE = 180

DTYPE = np.float32

# Get all model names in path
model_names = os.listdir(model_path)

# Initialise list to save all times

for model_name in model_names:
	times = []
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

	model_inshape = [N_PHOTOS] + RESOLUTION + [CHANNELS] # 10 bursts of resolution*resolution -> 3 channels
	model_outshape = [N_PHOTOS + 1] # 10 probabilities each of 10 bursts

	# Resize input and output tensors (batch_size axis) based on how many images you'll feed at once (by default it's 1, let's leave it that way for now)
	# Might want to change it to 10 later if we decide to click 10 images in a burst and feed them all as a batch
	interpreter.resize_tensor_input(in_details[0]["index"], model_inshape)
	interpreter.resize_tensor_input(out_details[0]["index"], model_outshape)
	interpreter.allocate_tensors()
	# This `interpreter` object will be called later to perform inference

	# Camera tasks
	while iteration < N_PHOTOS:
		# Click pictures
		with picamera.PiCamera() as camera:
			camera.resolution = RESOLUTION
			camera.rotation = ROTATE
			camera.framerate = FRAME_RATE
			click = np.empty((RESOLUTION[0]*RESOLUTION[1]*CHANNELS), dtype=DTYPE) # 1D array to capture 1 photo at a time

			photos = np.array([]) # Initialise empty array to store all the captured photos

			while np.shape(photos)[0] < N_PHOTOS*RESOLUTION[0]*RESOLUTION[1]*CHANNELS:
				camera.capture(click, "rgb")
				photos = np.append(photos, click)

			camera.close()

		x = photos.reshape(model_inshape)
		x = x.astype(DTYPE)

		# Inference

		# To calculate time taken
		start = time.time()

		interpreter.set_tensor(in_details[0]["index"], x)
		interpreter.invoke()
		pred = interpreter.get_tensor(out_details[0]["index"])
		
		# Time taken
		times.append(time.time()-start)

		print(pred)
		iteration += 1
		print(iteration)

	print(sum(times)/len(times))

	with open(os.path.join(save_path, save_file_name), "a") as f:
		f.write(f"{model_name}, {sum(times)/len(times)}\n")

	# Delete tflite and interpreter to free memory
	del tflite_model
	del interpreter
	gc.collect()
