import random
import sys

population = bytes([i for i in range(256)])

if sys.argv[1] == 'reflector':
    popset = set(population)
    buffer = [None for i in range(256)]
    for i in range(128):
        x, y = random.sample(popset, 2)
        popset.remove(x)
        popset.remove(y)
        buffer[x] = y
        buffer[y] = x
    print(bytes(buffer))

elif sys.argv[1] == 'rotor':
    print(bytes(random.sample(population, 256)))
