# Read HDF5
import h5py
import numpy as np
import matplotlib.pyplot as plt

#if not plt.isinteractive():
#    plt.ion()

path = 'c:\\EMBL data\\'
filename = 'EMBL_FullData_3channel.hdf'
print(path + filename)

with h5py.File(path + filename, 'r') as f:
    # List all groups
    print("Keys: %s" % f.keys())
    a_group_key = list(f.keys())[0]

    image_data_set = f['data/gallery']
    plt.imshow(image_data_set[:, :, 0:3, 0], cmap='gray')
    plt.show()
# )
print(type(image_data_set))
# plot the imagetest
# image_test = image_data_set[:, :, :, 0][()]

# plt.imshow(image_test[:, :, 0])
# plt.imshow(np.ones((25,25)))
# plt.show()
# print(image_data_set.shape())
