from nr_logical import *

expWidth, manWidth = 8, 16
rand_flt_a = random.uniform(0.001,pow(2,manWidth))
rand_flt_b = random.uniform(0.001,pow(2,manWidth))
rand_flt_a = random.uniform(0.001,10)
rand_flt_b = random.uniform(0.001,10)

print("floata, floatb")
print(rand_flt_a, rand_flt_b)
logicFloatA, logicFloatB = float_to_Logicfloat(rand_flt_a, expWidth, manWidth), float_to_Logicfloat(rand_flt_b, expWidth, manWidth)
print("floataLog, floatbLog")
print(logicFloatA, logicFloatB)
logicFloatPrime = multiplyLogicFloat(logicFloatA, logicFloatB, expWidth, manWidth)
floatOut = logicFloat_to_float(logicFloatPrime, expWidth, manWidth)
rand_fltPrime = rand_flt_a*rand_flt_b
if(abs(rand_fltPrime-floatOut)>2):
    print("errro:")
    print(rand_flt_a, rand_flt_b, rand_fltPrime)
    print(logicFloatA, logicFloatB, logicFloatPrime, floatOut)
    print(floatOut)
    exit(111)