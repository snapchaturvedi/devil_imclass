#======================================================================================
# Version 6
# Date: 04MAY2024
# Comments: 
### Use MobileNetv3small.tflite to detect devils and dispense bait
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
import gc
 
# Paths
program_path = "~/devil_imclass/programs"
model_path = "~/devil_imclass/models"
save_path = "~/devil_imclass/save"

# Camera config
n_photos = 10
channels = 3
resolution = [224, 224]

frame_rate = 50
rotate = 90

# Save inference times
times = []

# PIR object
pir = gpiozero.MotionSensor(4)

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
with open(os.path.join(model_path, "mnetv3s.tflite"), 'rb') as fid:
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

# DEVIL DETECTOR
try:
	while True:
		# Detect motion
		print("Waiting for motion")
		pir.wait_for_motion()
		print(f"Motion detected")

		# To calculate time taken
		start = time.time()	

		# Click pictures
		with picamera.PiCamera() as camera:
			camera.resolution = resolution
			camera.rotation = rotate
			camera.framerate = frame_rate
			click = np.empty((resolution[0]*resolution[1]*channels), dtype=np.uint8) # 1D array to capture 1 photo at a time
			
			photos = np.array([]) # Initialise empty array to store all the captured photos
			
			camera.start_preview()
			
			while np.shape(photos)[0] < n_photos*resolution[0]*resolution[1]*channels:
				camera.capture(click, "rgb")
				photos = np.append(photos, click)
			
			camera.stop_preview()

		x = photos.reshape(model_inshape)
		x = x.astype("float32")

		# Inference
		interpreter.set_tensor(in_details[0]["index"], x)
		interpreter.invoke()
		pred = interpreter.get_tensor(out_details[0]["index"])
		
		# Time taken for inference
		times.append(time.time()-start)
		
		print(pred)
		
		print(sum(pred>0.5))
		
		if sum(pred>0.5)>=5:
			print("Devil detected!")
			# devil=True
			
			while devil==True:
				print("Carousel start")

				carousel.start(pwr)

				if GPIO.input(switch_pin)==GPIO.HIGH:
					count = 1
					print(count)
					
					if GPIO.input(switch_pin)==GPIO.LOW:
						count = 2
						print(count)
						carousel.stop()
						devil=False
			
			print("Bait dispensed, going to sleep for 10s")
			time.sleep(10)
			
		else:
			print("Devil not detected")
			devil = False				
			
		# PIR wait for no motion before detecting movement again
		print("Waiting for no motion")
		pir.wait_for_no_motion()
		
		# Display when sleep over
		print("Ready to detect motion again\n")
except KeyboardInterrupt:
	GPIO.cleanup()
