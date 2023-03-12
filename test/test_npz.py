from tempfile import TemporaryFile
import numpy as np

x = [[1, 2, 3], [4, 5, 6]]
y = [1, 2, 3]

np.savez('temp.npz', x=x, y=y)
npfile = np.load('temp.npz')

print('x=', npfile['x'])

print('y=', npfile['y'])
