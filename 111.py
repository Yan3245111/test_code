import os
import pydicom

path = os.path.expanduser("~") + "\spine\dataStore\dicom_data"

ds = pydicom.dcmread(path + "/377.dcm")
pixel = ds.pixel_array  # 灰度值
slope = ds.RescaleSlope
intercept = ds.RescaleIntercept

hu_pixel = pixel * slope + intercept

print(hu_pixel[:2, :1])
