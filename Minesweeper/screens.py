from PIL import ImageGrab
import cv2
import numpy as np


while True:
    screen = np.array(ImageGrab.grab(bbox=(21,202,766,947)))
    # fix rgb to bgr
    screen = cv2.cvtColor(screen, cv2.COLOR_RGB2BGR)
    cv2.imshow('Python Window', screen)
    # add title 
    cv2.setWindowTitle('Python Window', 'Python Window')

    if cv2.waitKey(25) & 0xFF == ord('q'):
        cv2.destroyAllWindows()
        break
