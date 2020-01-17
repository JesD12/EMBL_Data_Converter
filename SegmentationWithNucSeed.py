##Load the files
# 1. the images files with the secondary marker (actin, tubulin or mytochondria)
# 2. the segmented and classified nucleus image

# import the libraries
import h5py
import numpy as np
import matplotlib.pyplot as plt
import cv2


def show_n_images(*images):
    f, axarr = plt.subplots(1, len(images))  # we need length of input images in a row
    for idx, image in enumerate(images, start=0):
        axarr[idx].imshow(image, cmap='gray')
    _ = [ax.axis('off') for ax in axarr]  # remove the axis ticks
    plt.show()


def transfergroundtruth(GT_image, NewImage, ThresholdValue=0, AdaptiveThreshold=False):
    # generate a threshold image
    if AdaptiveThreshold:
        _, thresh_manual = cv2.threshold(NewImage.astype('uint8'), 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    else:
        _, thresh_manual = cv2.threshold(NewImage, ThresholdValue, 255, cv2.THRESH_BINARY)

    sure_bg = np.uint8(thresh_manual)
    _, sure_fg = cv2.threshold(GT_image.astype('uint8'), 0, 255, cv2.THRESH_BINARY)
    sure_fg = np.uint8(sure_fg)

    # unknwon define the area we want the watershed to fill out (the segmenented - the nucleus we know)
    # it has to be zero in
    unknown = cv2.subtract(sure_bg, sure_fg)
    markers = np.uint8(GT_image) + 1
    markers[unknown == 255] = 0
    watershedImage = cv2.cvtColor(NewImage.astype('uint8'), cv2.COLOR_GRAY2RGB)
    GroundTruthImage = cv2.watershed(watershedImage, markers.astype('int32'))
    GroundTruthImage[GroundTruthImage == -1] = 1
    return np.uint8(GroundTruthImage - 1)


path = 'e:\\EMBL data\\Jes 3D 3C plate 2__2019-12-11T10_29_03-Measurement 1\\Classification_Ilastik\\'
filenameNuc = 'r01c03f06_5frames_MIP_GT.h5'
filename2ch = 'r01c03f06_5frames_MIP.h5'

rows = ['r01', 'r02', 'r03','r04', 'r05', 'r06', 'r07', 'r08']
columns = ['c01', 'c02', 'c03', 'c04', 'c05', 'c06', 'c07', 'c08', 'c09', 'c10', 'c11', 'c12']
fields = ['f01', 'f02', 'f03', 'f04', 'f05', 'f06', 'f07', 'f08','f09']

for Labelindex, row in enumerate(rows):
    for Conditionindex, column in enumerate(columns):
        if Conditionindex < 4:
            Conditionfolder = 'Control\\'
        elif Conditionindex < 8:
            Conditionfolder = 'KiF23\\'
        else:
            Conditionfolder = 'ESPL\\'

        for field in fields:
            filenameNuc = row + column + field + '_5frames_MIP_new_GT.h5'
            filename2ch = row + column + field + '_5frames_MIP.h5'
            # print(filenameNuc)
            # meed to load 3 files:
            # A: image with segmented and annotated nucleus,
            # B: Image with the actin channel common for all
            # C: channel with the green 'variable' channel

            # A
            with h5py.File(path + Conditionfolder + "Nucleus\\" + filenameNuc, 'r') as fNuc:
                NucleusImageData = fNuc['exported_data'][()]
            SegmentedNucleus = NucleusImageData[0, 0, :, :, 0]

            # B
            with h5py.File(path + Conditionfolder + "actin_2ch\\" + filename2ch, 'r') as fAct:
                ImageDataActin = fAct['data'][()]
            # extract the two channels
            Actin = ImageDataActin[0, 0, :, :, 1]
            nucleus = ImageDataActin[0, 0, :, :, 0]
            ActNuc = Actin + nucleus

            # Transfer the groundtruth
            GroundTruthImageAct = transfergroundtruth(SegmentedNucleus, Actin, 300)
            # show_n_images(SegmentedNucleus, bothchannels, GroundTruthImage)
            GroundTruthExportAct = np.zeros((NucleusImageData.shape), 'uint8')
            GroundTruthExportAct[0, 0, :, :, 0] = GroundTruthImageAct

            # save the new h5 file

            with h5py.File(path + Conditionfolder + "actin_2ch\\" + filenameNuc, 'w') as fNew:
                fNew.create_dataset('exported_data', shape=GroundTruthExportAct.shape, data=GroundTruthExportAct)

            # C
            # determine what kind the green signal is (mito, tubulin or chromatin)
            # Chromatin is a special case as the nucleus mask will just be used
            if row == 'r03' or row == 'r04':
                subfolder = "Cromatin_2ch\\"
            elif row == 'r07' or row == 'r08':
                subfolder = "Mito_2ch\\"
                GFPThreshold = 300
            else:
                subfolder = "Tub_2ch\\"
                GFPThreshold = 300

            if subfolder == "Cromatin_2ch\\":
                GroundTruthExportGFP = NucleusImageData
            else:
                with h5py.File(path + Conditionfolder + subfolder + filename2ch, 'r') as fGFP:
                    ImageDataGFP = fGFP['data'][()]
                # extract the two channels
                GFP = ImageDataGFP[0, 0, :, :, 1]
                nucleus = ImageDataGFP[0, 0, :, :, 0]
                GFPNuc = GFP + nucleus

                # transfer the groundtruth
                GroundTruthImageGFP = transfergroundtruth(SegmentedNucleus, GFP, GFPThreshold)
                # show_n_images(SegmentedNucleus, bothchannels, GroundTruthImage)
                GroundTruthExportGFP = np.zeros((NucleusImageData.shape), 'uint8')
                GroundTruthExportGFP[0, 0, :, :, 0] = GroundTruthImageGFP

            with h5py.File(path + Conditionfolder + subfolder + filenameNuc, 'w') as fNewGFP:
                fNewGFP.create_dataset('exported_data', GroundTruthExportGFP.shape, data=GroundTruthExportGFP)

            #if field == 'f09':
            #    show_n_images(SegmentedNucleus, ActNuc, GroundTruthImageAct, GFPNuc, GroundTruthImageGFP)

        print(f'Just finished row: {row}, column: {column}')
