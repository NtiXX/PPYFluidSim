import numpy as np

# Offsets for finding neighbours of cells
offsets = [
    np.array([-1, 1]), # Bottom Left
    np.array([0, 1]), # Bottom
    np.array([1, 1]), # Bottom Right
    np.array([-1, 0]), # Left
    np.array([0, 0]), # Center / Given cell
    np.array([1, 0]), # Right
    np.array([-1, -1]), # Top left
    np.array([0, -1]), # Top
    np.array([1, -1]), # Top right
]

# Random values used for hashing
hashK1 = 15823
hashH2 = 9737333

def GetCell(point, radius):
    """ 
    Computes cell coordinates for given point in grid
    Returns: Array of integer coordinates [cellX, cellY]
    """
    return [int(point[i] / radius) for i in range(2)]

def HashCell(cell):
    """ 
    Computes pseudo random hash function 
    Purpose: Defining a cell by a single number
    Return: Hash as integer
    """
    a = cell[0] * hashK1
    b = cell[1] * hashH2

    return int(a + b)

def GetKeyFromHash(cellHash, tableSize):
    """ 
    Computes cell key for the hash table from a cell hash
    Returns: Cell key as an integer
    """
    return int(cellHash % tableSize)