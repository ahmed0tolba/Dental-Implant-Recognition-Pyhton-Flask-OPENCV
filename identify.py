# pip install opencv-contrib-python==4.1.2.30 opencv-python==4.1.2.30 tensorflow
import numpy
import tensorflow as tf
import cv2 as cv
from matplotlib import pyplot as plt
import math
from scipy import ndimage
import numpy as np
def getImplantType(SaveDir,imgName,thresholdbw):
    features = getImplantValues(SaveDir,imgName,thresholdbw)
    print(features)
    features1 = numpy.array([features[:]])
    print(features1)
    loaded_model = tf.keras.models.load_model('model.model')
    prediction = loaded_model.predict(features1)
    print(prediction)
    return prediction

def getImplantValues(SaveDir,imgName,thresholdbw):
  img =  cv.imread(SaveDir+imgName)[:,:,0]
  # print("img")
  # cv2_imshow(img)
  blured = cv.blur(img,(10,10)) 
  # print("blured")
  # cv2_imshow(blured)

  if thresholdbw==0:
    thresholdbw = img.mean(axis=0).mean(axis=0)

  (thresh, BWFilling) = cv.threshold(blured, thresholdbw, 255, cv.THRESH_BINARY)
  cv.imwrite(SaveDir+"BW_"+imgName, BWFilling)
  # print("BWFilling")
  # cv2_imshow(BWFilling)




  contours, hierarchy = cv.findContours(BWFilling,cv.RETR_LIST,cv.CHAIN_APPROX_SIMPLE)[-2:]
  idx = 0
  idy = 0
  contours_filter1=[]
  contours_filter1_box=[]
  contours_filter1_center=[]
  contours_filter1_angle=[]
  dist_from_edge_to_curve=0
  for cnt in contours:  
    idx += 1
    x,y,w,h = cv.boundingRect(cnt)    
    if ( (w>100 or h >100) and w+h>200):
      contours_filter1.append(cnt)
      contours_filter1_box.append([x,y,w,h])
      contours_filter1_center.append([x+w/2, y+h/2])
      crop_impant = BWFilling[contours_filter1_box[idy][1]-0:contours_filter1_box[idy][1] + contours_filter1_box[idy][3]+0, contours_filter1_box[idy][0]-0:contours_filter1_box[idy][0]+contours_filter1_box[idy][2]+0]
      # print("contour number: ", idy)
      # print("crop_impant")
      # cv2_imshow(crop_impant)
      angle = 0
      Saturated = False
      
      max=100
      c=0
      direction = 0
      directionold = 0
      while (not Saturated):
        directionold = direction
        c +=1
        rotatedPlus = ndimage.rotate(crop_impant, 1+angle)
        xp,yp,wp,hp = cv.boundingRect(rotatedPlus)
        rotatedMinus = ndimage.rotate(crop_impant, -1+angle)
        xm,ym,wm,hm = cv.boundingRect(rotatedMinus)
        if (wp<wm):
          angle +=1
          direction = 1
        if (wp>wm):
          angle -=1
          direction = -1
        if (c>max or wp==wm or (direction != 0 and direction ==- directionold)): # exit 
          Saturated = True
          
      # print("angle ",angle)

      rotated = ndimage.rotate(crop_impant, angle)
      x,y,w,h = cv.boundingRect(rotated)
      # print("rotated ")
      # cv2_imshow(rotated)

      if (w > h):
        rotated = ndimage.rotate(crop_impant, 90)
        x,y,w,h = cv.boundingRect(rotated)      
      
      
      crop_rotated_impant = np.zeros((h+10,w+10), np.uint8)
      crop_rotated_impant[5:y+h+5,5:x+w+5] = rotated[y:y+h, x:x+w]
      # crop_rotated_impant = rotated[y-5:y+h+5, x-5:x+w+5]

      edges = cv.Canny(crop_rotated_impant,100,200)
      contours1, hierarchy = cv.findContours(edges,cv.RETR_LIST,cv.CHAIN_APPROX_SIMPLE)[-2:]
      # print("edges")
      # cv2_imshow(edges)

      for contour in contours1:
        # print("cotlen ", len(contour))
        if ( len(contour)>200):
          topleftpoint = []
          topleftdist = 9999
          toprightpoint = []
          toprightdist = 9999
          bottomleftpoint = []
          bottomleftdist = 9999
          bottomrightpoint = []
          bottomrightdist=9999
          for point in contour:
            distthispointtopleft = (((0 - point[0][0] )**2) + ((0-point[0][1])**2) )**0.5
            distthispointtopright = (((x+w+5 - point[0][0] )**2) + ((0-point[0][1])**2) )**0.5
            distthispointbottomleft = (((0 - point[0][0] )**2) + ((y+h+5-point[0][1])**2) )**0.5
            distthispointbottomright = (((x+w+5 - point[0][0] )**2) + ((y+h+5-point[0][1])**2) )**0.5
            if distthispointtopleft < topleftdist :
              topleftdist = distthispointtopleft
              topleftpoint = point[0]
            if distthispointtopright < toprightdist :
              toprightdist = distthispointtopright
              toprightpoint = point[0]
            if distthispointbottomleft < bottomleftdist :
              bottomleftdist = distthispointbottomleft
              bottomleftpoint = point[0]
            if distthispointbottomright < bottomrightdist :
              bottomrightdist = distthispointbottomright
              bottomrightpoint = point[0]
          
          dist_up = (((topleftpoint[0] - toprightpoint[0] )**2) + ((topleftpoint[1]-toprightpoint[1])**2) ) ** 0.5
          dist_down = (((bottomleftpoint[0] - bottomrightpoint[0] )**2) + ((bottomleftpoint[1]-bottomrightpoint[1])**2) ) **0.5

          cv.circle(edges, (topleftpoint[0],topleftpoint[1]), 5, (100, 100, 100), 2)
          cv.circle(edges, (toprightpoint[0],toprightpoint[1]), 5, (100, 100, 100), 2)
          cv.circle(edges, (bottomleftpoint[0],bottomleftpoint[1]), 5, (100, 100, 100), 2)
          cv.circle(edges, (bottomrightpoint[0],bottomrightpoint[1]), 5, (100, 100, 100), 2)
          print((edges.shape))
          ninety_percent_dist_to_intersection_point=0
          flop180 = False
          if (dist_down + dist_up > w):
            if dist_up >= dist_down:# and dist_down + dist_up > 100:
              flop180 = True
              dist_from_edge_to_curve = ( distthispointbottomleft + distthispointbottomright ) / 2 / w
              widthratio = dist_down / w
              ydown = round((bottomleftpoint[1]+bottomrightpoint[1])/2); 
              widthydown = bottomrightpoint[0]-bottomleftpoint[0]
              ninety_percent_dist_to_intersection_point = widthydown
              yup_ninety_percent_dist = ydown
              while ninety_percent_dist_to_intersection_point < 0.8 * w:
                ydown -=1
                firstloc = 0
                firstrecorded = False
                secondloc = 0
                secondrecorded = False
                count = 0
                previouspoint=0
                for point in edges[ydown][:]:
                  if (count>1):
                    if (point==255 and firstrecorded and edges[ydown][count-1]==0):
                      secondrecorded = True
                      secondloc = count                    
                      ninety_percent_dist_to_intersection_point = secondloc - firstloc
                      yup_ninety_percent_dist = ydown

                    if (point==255 and not firstrecorded and edges[ydown][count-1]==0):
                      firstrecorded = True
                      firstloc = count                    
                  previouspoint = point
                  count += 1
              edges = cv.line(edges, (0,ydown), (w,ydown), (100, 255, 100), 1)

            else: # dist_up < dist_down
              dist_from_edge_to_curve = ( distthispointtopleft + distthispointtopright ) / 2 / w
              widthratio = dist_up / w 
              yup = round((topleftpoint[1]+toprightpoint[1])/2); 
              widthyup = toprightpoint[0]-topleftpoint[0]
              ninety_percent_dist_to_intersection_point = widthyup
              yup_ninety_percent_dist = yup
              while ninety_percent_dist_to_intersection_point < 0.8 * w:
                yup +=1
                firstloc = 0
                firstrecorded = False
                secondloc = 0
                secondrecorded = False
                count = 0
                previouspoint=0
                for point in edges[yup][:]:
                  if (count>1):
                    if (point==255 and firstrecorded and edges[yup][count-1]==0):
                      secondrecorded = True
                      secondloc = count                    
                      ninety_percent_dist_to_intersection_point = secondloc - firstloc
                      yup_ninety_percent_dist = yup

                    if (point==255 and not firstrecorded and edges[yup][count-1]==0):
                      firstrecorded = True
                      firstloc = count                    
                  previouspoint = point
                  count += 1
              edges = cv.line(edges, (0,yup), (w,yup), (100, 255, 100), 1)

          # print("edges")
          
        #   cv2_imshow(edges)

      idy +=1
  print("widthratio",widthratio,"yup_ninety_percent_dist%",yup_ninety_percent_dist/w)
  return [widthratio, yup_ninety_percent_dist/w]