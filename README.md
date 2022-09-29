<p align="center">
  <a>
    <img src="https://raw.githubusercontent.com/th33xitus/PrusaSlicerThumbnailPostProcessor/master/images/image.png" alt="benchy" height="181">
    <h1 align="center">PrusaSlicer Thumbnail Post-Processor</h1>
  </a>
</p>

<p align="center">
  An experimental, python based post-processing script, to try and compensate for a (personally) much missed feature in PrusaSlicer.
</p>

<p align="center">
  <a><img src="https://img.shields.io/github/license/th33xitus/PrusaSlicerThumbnailPostProcessor"></a>
  <a><img src="https://img.shields.io/github/stars/th33xitus/PrusaSlicerThumbnailPostProcessor"></a>
  <a><img src="https://img.shields.io/github/forks/th33xitus/PrusaSlicerThumbnailPostProcessor"></a>
  <a><img src="https://img.shields.io/github/languages/top/th33xitus/PrusaSlicerThumbnailPostProcessor?logo=python&logoColor=white"></a>
  <a><img src="https://img.shields.io/github/last-commit/th33xitus/PrusaSlicerThumbnailPostProcessor"></a>
  <a><img src="https://img.shields.io/github/contributors/th33xitus/PrusaSlicerThumbnailPostProcessor"></a>
</p>

## **📄 Description:**
The script reads the original thumbnail and the filament color the G-Code was sliced with.
It then modifies the original thumbnail and replaces the orange'ish default color by the filament color.
After that it rewrites the thumbnail data and appends it at the very end of the file.

## **🛠️ Instructions:**

For the script to properly work, you need to have Python 3.9 and Pillow 9.2.0 installed.\
Download the script to your preferred location and add its path to PrusaSlicers post-processing input.

Example (Windows):
```
python3 C:\User\Desktop\PrusaSlicerThumbnailPostProcessor\pstnpp.py;
```
In case you want to remove the thumbnail background, append `-nb`:
```
python3 C:\User\Desktop\PrusaSlicerThumbnailPostProcessor\pstnpp.py -nb;
```

## **❗ Notes:**

- Image quality might vary depending on colors
- Only a single thumbnail resolution is supported, do not use multiple different resolutions
- Issues might occur when using custom bed shape models or textures with other colors than gray


