#======================================================================================
# Version 7
# Date: 11JUN2024
# Comments: 
### Detect devils and dispense baits
#======================================================================================

# Load libraries
import os
import time
import gpiozero
import RPi.GPIO as GPIO
import numpy as np
import tflite_runtime.interpreter as tflite
import picamera
from PIL import Image
from datetime import datetime
 
# Paths
program_path = os.path.join(os.getcwd(), "devil_imclass", "programs")
model_path = os.path.join(program_path, "..", "models")
save_path = os.path.join(program_path, "..", "save")
log_path = os.path.join(program_path, "..", "log")

# Create paths if does not exist
paths = [save_path, log_path]
for path in paths:
	if not os.path.exists(path):
			os.mkdir(path)
		
# Create log file if does not exist
if not os.path.exists(os.path.join(log_path, "log.csv")):
	with open(os.path.join(log_path, "log.csv"), "w") as file:
		file.write("event, timestamp\n")

# Camera config
N_PHOTOS = 10
CHANNELS = 3
RESOLUTION = [1024, 768]
MODEL_IMG_SHAPE = [224, 224]
ROTATE = 180

# PIR object
PIR = gpiozero.MotionSensor(4)
SLEEP_TIME = 5

# Carousel
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# Motor
frq = 100
pwr = 100
motor_pin = 18
GPIO.setup(motor_pin, GPIO.OUT)
carousel = GPIO.PWM(motor_pin, frq)

# Switch
switch_pin = 3
GPIO.setup(switch_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Load tflite model
with open(os.path.join(model_path, "model2.keras.tflite"), 'rb') as fid:
	tflite_model = fid.read()

# Load interpreter
interpreter = tflite.Interpreter(model_content=tflite_model)
interpreter.allocate_tensors()
in_details = interpreter.get_input_details()
out_details = interpreter.get_output_details()

# In and out data dimensions for interpreter
model_inshape = [N_PHOTOS] + MODEL_IMG_SHAPE + [CHANNELS]
model_outshape = [N_PHOTOS + 1]

# Resize input and output tensors (batch_size axis) based on how many images you'll feed at once (by default it's 1, let's leave it that way for now)
interpreter.resize_tensor_input(in_details[0]["index"], model_inshape)
interpreter.resize_tensor_input(out_details[0]["index"], model_outshape)
interpreter.allocate_tensors()

# Thresholds for inference
THRESH = 0.5			# To classify devil vs bg
N_PREDS = N_PHOTOS/2		# No. of images that are predicted devil

# Function to log progression
def logprog(event):
	# Log event
	with open(os.path.join(log_path, "log.csv"), "a") as file:
		file.write(f"{event}, {datetime.now()}\n")

# Function to click pictures
def click_pictures():

	# Empty arrays to store individual pictures and all the clicks
	click = np.empty((RESOLUTION[0]*RESOLUTION[1]*CHANNELS), dtype=np.uint8)
	photos = np.array([], dtype=np.uint8)
	
	# Start clicking (sensor_mode=4 is HD with full view)
	with picamera.PiCamera(sensor_mode=4) as camera:
		
		# Pause for some time to let camera adjust focus
		time.sleep(2)

		# Take n_photos 
		while np.shape(photos)[0] < N_PHOTOS*RESOLUTION[0]*RESOLUTION[1]*CHANNELS:
			camera.capture(click, "rgb")
			photos = np.append(photos, click)

	# Reassemble the pictures clicked		
	photos2 = photos.reshape([n_photos, RESOLUTION[1], RESOLUTION[0], CHANNELS])

	# Resize pictures for the interpreter
	photos3 = np.array([])
	for i in range(N_PHOTOS):
		picture = Image.fromarray(photos2[i,:,:,:]).resize(MODEL_IMG_SHAPE)
		picture.save(os.path.join(save_path, f"{datetime.now()}.png"))
		photos3 = np.append(photos3, np.array(picture))
	photos3 = photos3.reshape([N_PHOTOS, MODEL_IMG_SHAPE[0], MODEL_IMG_SHAPE[0], CHANNELS])
	
	# Update datatype to float32 for interpreter
	photos4 = photos3.astype("float32")
	
	return photos4

# Function to use interpreter
def predict(indata):
	# Set and invoke interpreter
	interpreter.set_tensor(in_details[0]["index"], indata)
	interpreter.invoke()
	pred = interpreter.get_tensor(out_details[0]["index"])
	return pred
	
# Function to drop bait
def dispense_bait(devil=True, attempt=0, attempt_thresh=5, time_thresh=4):
	start = time.time()
	status = ""
	while time.time()-start <= time_thresh:
		if attempt <= attempt_thresh:
			print(f"Carousel start attempt {attempt}")
			carousel.start(pwr)
			
			if GPIO.input(switch_pin)==GPIO.HIGH:
				if GPIO.input(switch_pin)==GPIO.LOW:
					carousel.stop()
					status = "success"
					logprog(f"{status}")
					break
		
		else:
			logprog("failure")
			break
			
	
	if time.time()-start > time_thresh:
		dispense_bait(attempt=attempt+1)
	
	if status == "success":
		print("Bait dispensed, going to sleep")
		time.sleep(sleep_time)

		print("Waiting for no motion")
		PIR.wait_for_no_motion()

# Run the process
try:
	while True:
		# Detect motion
		print("Waiting for motion")
		PIR.wait_for_motion()
		logprog("motion")
		
		# Click pictures
		photos = click_pictures()

		# Make predictions
		pred = predict(photos)

		# Infer on predictions
		if sum(pred>THRESH)>=N_PREDS:
			print("Devil detected")
			dispense_bait()			
			
except KeyboardInterrupt:
	GPIO.cleanup()
