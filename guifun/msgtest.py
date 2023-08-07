



from msgpack import packb, unpackb
from array import array
arr = array('f', [1,2,3])
byt = arr.tobytes()


x = packb({'msg' : byt})
orig = unpackb(x)
arr2 = array('f')
arr2.frombytes(orig['msg'])
print(arr2)