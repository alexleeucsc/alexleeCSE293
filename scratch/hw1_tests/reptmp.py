from nr_logical import *
#test logicFloat_to_float and float_to_Logicfloat
rand_flt, expWidth, manWidth = 93.5, 100, 640
rand_flt = 93.0
#bug 1: the random float has to fit entirely in the mantisa:
#otherwise, it will be off by a large number
logicFloat = float_to_Logicfloat(rand_flt, expWidth, manWidth)
print(logicFloat)
floatOut = logicFloat_to_float(logicFloat, expWidth, manWidth)
print(floatOut)
assert(abs(rand_flt-floatOut)<1.5)