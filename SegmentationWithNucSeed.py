##Load the files
# 1. the images files with the secondary marker (actin, tubulin or mytochondria)
# 2. the segmented and classified nucleus image

# import the libraries
import h5py
import numpy as np
import matplotlib.pyplot as plt
import cv2

path = 'c:\\EMBL data\\'
filenameNuc = 'r01c01f03_5frames_MIP_GT.h5'  # this should be doublechecked.
filename2ch = 'r01c01f03_5frames_MIP.h5'  # this should be doublechecked.


def show_n_images(*images):
    f, axarr = plt.subplots(1, len(images))  # we need length of input images in a row
    for idx, image in enumerate(images, start=0):
        axarr[idx].imshow(image, cmap='gray')
    _ = [ax.axis('off') for ax in axarr]  # remove the axis ticks
    plt.show()


with h5py.File(path + "nucleus test\\" + filenameNuc, 'r') as fNuc:
    # print("Keys: %s" % fNuc.keys())
    NucleusImageData = fNuc['exported_data_probability'][()]

with h5py.File(path + "actin_2ch\\" + filename2ch, 'r') as fGFP:
    # print("Keys: %s" % fGFP.keys())
    ImageData2Channel = fGFP['data'][()]

plt.imshow(NucleusImageData[0, 0, :, :, 0])
SegmentedNucleus = NucleusImageData[0, 0, :, :, 0]
plt.show()
Actin = ImageData2Channel[0, 0, :, :, 1]
nucleus = ImageData2Channel[0, 0, :, :, 0]
bothchannels = Actin + nucleus
show_n_images(Actin, nucleus, bothchannels,SegmentedNucleus)
# Maxvalue= np.amax(Actin)
# bothNorm= bothchannels/np.amax(bothchannels) * 255
# bothEnhanced = bothchannels/np.quantile(bothchannels,0.5)*255
# print(bothEnhanced.max())
# bothEnhanced[bothEnhanced > 255] = 255
# plt.imshow(bothEnhanced)
# plt.show()
# print(bothEnhanced.max())
# print(bothchannels.max())
# print(np.quantile(bothchannels,[0.5,0.8,0.9,0.95,0.99]))
# hist, bin_edge = np.histogram(bothchannels, 100)
# hist_norm, bin_edge_norm = np.histogram(bothNorm, 100)
# hist_en, bin_edge_en = np.histogram(bothEnhanced, 100)
# plt.plot(bin_edge[1:], hist,  bin_edge[1:], hist_en, bin_edge[1:], hist_norm)

# create a way to segment the image (this could be made easier by segmenting in ilastik)
# ret, thresh_raw = cv2.threshold(bothchannels.astype('uint8'),0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
# ret, thresh_normalized = cv2.threshold(bothNorm.astype('uint8'),0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
# ret, thresh_enhanced = cv2.threshold(bothEnhanced.astype('uint8'),0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
ret, thresh_manual = cv2.threshold(bothchannels, 500, 255, cv2.THRESH_BINARY)
# show_n_images(thresh_raw, thresh_normalized, thresh_enhanced, thresh_manual)
# plt.show()
sure_bg = np.uint8(thresh_manual)
ret, sure_fg = cv2.threshold(SegmentedNucleus.astype('uint8'),0,255,cv2.THRESH_BINARY)
sure_fg = np.uint8(sure_fg)
unknown = cv2.subtract(sure_bg, sure_fg)
show_n_images(SegmentedNucleus, sure_bg, sure_fg, unknown)
markers = np.uint8(SegmentedNucleus)+1
markers[unknown == 255] = 0
plt.imshow(markers, cmap = 'jet')
watershedImage = cv2.cvtColor(bothchannels.astype('uint8'), cv2.COLOR_GRAY2RGB)
GroundTruthImage = cv2.watershed(watershedImage, markers.astype('int32'))
GroundTruthImage = np.uint8(GroundTruthImage+1)
show_n_images(markers, GroundTruthImage)
