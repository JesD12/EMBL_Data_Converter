# Read HDF5
import h5py
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import csv

def savetheimage(imagetosave,filename, category= 'Healthy',savepath = 'C:\\EMBLE data\\Data\\', valprocent = 0.2):
    im = Image.fromarray(imagetosave)
    #determine whether it should be saved as a training or validation
    #if it need to be the same for nuc and actin put an output on this that
    #function as an input next time this funtion is run
    subfolder = 'TRAIN\\'
    if np.random.uniform() < valprocent:
        subfolder = 'VAL\\'
    im.save(savepath+subfolder+category+'\\'+filename+'.png')

ImageFile = 'C:\\EMBL data\\Jes 3D 3C plate 2__2019-12-11T10_29_03-Measurement 1\\CellCogData\\EMBL_FullData_3channel.hdf'
SavePath = 'C:\\EMBL data\\Data\\'
csvpath = 'C:\\EMBL data\\Jes 3D 3C plate 2__2019-12-11T10_29_03-Measurement 1\\CellCogData\\TableData_full\\'
csvfilename = 'EMBL_FullData_3channel_'
Classifyerlist = ['Healthy', 'Binucleated', 'Big', 'Mitotic']

with h5py.File(ImageFile, 'r') as f:
    image_data_set = f['data/gallery']
    #Set up a for loop to go over all 3 csv files
    i = 0
    missed = 0
    for csvidx in range(1, 4):
        with open(csvpath + csvfilename + f'{csvidx}of3.csv') as csvfile:
            print(f'Starting on {csvidx} of 3')
            csv_reader = csv.reader(csvfile,delimiter = ',')
            #skip the header row
            next(csv_reader,None)
            for row in csv_reader:
                #check whether the image is classified
                if int(row[4]) in range(4):
                    cat = Classifyerlist[int(row[4])]
                    filename = f'Image_{i:05d}'
                    #save the nuclues image
                    savetheimage(image_data_set[:, :, 0, i],filename, category=cat, savepath=SavePath+'Nucleus\\')
                    # saveActin
                    savetheimage(image_data_set[:, :, 2, i],filename,category= cat, savepath=SavePath+'Actin\\')
                else:
                    missed += 1
                #check-up
                if i%500 == 0:
                    print(f'ID: {row[0]} is {row[3]} and therefore a number: {row[4]}')
                    print(f'determined as image number {i:05d} and put into the {cat} group')
                    if missed > 0:
                        print(f'currently we have skipped :{missed}')
                i += 1



        #saveNucleus
        #savetheimage(image_data_set[:, :, 0, i],filename,savepath=SavePath+'Nucleus\\')
        #saveActin
        #savetheimage(image_data_set[:, :, 2, i],filename,savepath=SavePath+'Actin\\')






