import appdaemon.plugins.hass.hassapi as hass
import cv2
import numpy as np
import datetime
import requests
import urllib.request


class GasTankReader(hass.Hass):

  def initialize(self):
    time = datetime.datetime.now() + datetime.timedelta(seconds = 5)
    ##self.handle = self.run_minutely(self.get_reading, time)
    self.handle = self.run_every(self.get_reading, time, 5*60)

  def get_reading(self, kwargs):
    reading = self.process_image()
    self.log("Gas Reading: {} ".format(reading))
    self.call_service("mqtt/publish", topic = "wyzecam/gas_tank", payload= reading)
  
  def url_to_image(self, url):
    # https://www.pyimagesearch.com/2015/03/02/convert-url-to-image-with-python-and-opencv/
    #resp = urllib.urlopen(url)
    with urllib.request.urlopen(url) as url_img:
      image = np.asarray(bytearray(url_img.read()), dtype="uint8")
      image = cv2.imdecode(image, cv2.IMREAD_COLOR)
  # return the image
    return image

  def process_image(self):
    image = self.url_to_image(url = "http://192.168.100.50:8123/local/snap_gas.jpg")
    #image = np.asarray(bytearray(resp.read()), dtype="uint8")
    #image = cv2.imdecode(image, cv2.IMREAD_COLOR)
    #image
    #dst2 = cv2.medianBlur(image, 3)
    #dst2 = cv2.GaussianBlur(image, (3,3), 0)
    dst2 = image
    img_hsv=cv2.cvtColor(dst2, cv2.COLOR_BGR2HSV)

        # lower mask (0-10)
    lower_red = np.array([0,50,50])
    upper_red = np.array([20,255,255])
    mask0 = cv2.inRange(img_hsv, lower_red, upper_red)

        # upper mask (170-180)
    lower_red = np.array([120,50,50])
    upper_red = np.array([130,255,255])
    mask1 = cv2.inRange(img_hsv, lower_red, upper_red)

        # join my masks
    mask = mask0 #+mask1

        # set my output img to zero everywhere except my mask
    output_img = image.copy()
    output_img[np.where(mask==0)] = 0
    gray2 = cv2.cvtColor(output_img, cv2.COLOR_BGR2GRAY)
    res_write = cv2.imwrite("red.jpg",gray2)
    self.log("Sucess writing image: {}".format(res_write))
    img2 = image.copy()
    minLineLength = 400
    maxLineGap = 5
    lines = cv2.HoughLinesP(image=gray2, rho=1, 
        theta=3.1416 / 180, threshold=7, minLineLength= minLineLength, maxLineGap = maxLineGap)
    final_line_list = []

    x_center = 700
    y_center = 655
    
    cv2.circle(img2,(int(x_center),int(y_center)), 5, (0,0,255), -1)
    for line in lines:
        for x1, y1, x2, y2 in lines[0]:
            final_line_list.append([x1, y1, x2, y2])

    dist_max = 0
    i = -1
    self.log("Number of lines: {}".format(len(final_line_list)))
    for line in final_line_list:
        x1 = line[0]
        y1 = line[1]
        x2 = line[2]
        y2 = line[3]
        dist_pts = np.sqrt((y2-y1)**2 + (x2-x1)**2)
        cv2.line(img2, (x1, y1), (x2, y2), (0, 255, 0), 2)
        #dist_linea = abs(((y2-y1)*x_center - #x2-x1)*y_center+x2*y1-y2*x1))/dist_pts
        if(dist_pts > dist_max):
            i_min = i + 1
            dist_max = dist_pts


    self.log("Distance of longest line: {}".format(dist_max))
    i = i_min
    x1 = final_line_list[i][0] 
    y1 = final_line_list[i][1]
    x2 = final_line_list[i][2]
    y2 = final_line_list[i][3]
    dist1 = (x1 - x_center)**2 + (y1 - y_center)**2
    dist2 = (x2 - x_center)**2 + (y2 - y_center)**2
    cv2.line(img2, (x1, y1), (x2, y2), (255,0,0), 3)

    if dist1 > dist2:
        angle = np.arctan2(-(y1-y_center), x1-x_center) * 180 / np.pi
        cv2.circle(img2, (x1,y1), 5, (0,0,255), -1)     
    else:
        angle = np.arctan2(-(y2-y_center), x2-x_center) * 180 / np.pi
        cv2.circle(img2, (x2,y2), 5, (0,0,255), -1)
    cv2.imwrite("img_gauge.jpg", img2)
    self.log("Angle: {}".format(angle))
    if angle < 0:
        reading = -((60-22)/90.0)*(angle+90.0) - 15.0
    else:
        reading = ((50-80)/(90-24))*(angle - 24) + 75.0
    return reading  