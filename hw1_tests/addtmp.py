from nr_logical import *

expWidth, manWidth = 8, 16
rand_flt_a = random.uniform(0.001,pow(2,manWidth))
rand_flt_b = random.uniform(0.001,pow(2,manWidth))
rand_flt_a = random.uniform(0.001,10)
rand_flt_b = random.uniform(0.001,10)

# rand_flt_a, rand_flt_b = 1.7620020119137576, 0.8468884890148226
# rand_flt_a, rand_flt_b = 2.8267202377032286, 1.0737544389655895
# rand_flt_a, rand_flt_b = 2.1107202377032286, 1.0737544389655895
rand_flt_a, rand_flt_b = 9.570689649634707, 9.954071475580543
print("\n\n\n")
print("floata, floatb")
print(rand_flt_a, rand_flt_b)
logicFloatA, logicFloatB = float_to_Logicfloat(rand_flt_a, expWidth, manWidth), float_to_Logicfloat(rand_flt_b, expWidth, manWidth)
print("floataLog, floatbLog")
print(logicFloatA, logicFloatB)
logicFloatPrime = addLogicFloat(logicFloatA, logicFloatB, expWidth, manWidth)
floatOut = logicFloat_to_float(logicFloatPrime, expWidth, manWidth)
rand_fltPrime = rand_flt_a+rand_flt_b
print("out",rand_fltPrime)
if(abs(rand_fltPrime-floatOut)>2):
    print("errro:")
    print(rand_flt_a, rand_flt_b, rand_fltPrime)
    print(logicFloatA, logicFloatB, logicFloatPrime, floatOut)
    print(floatOut)
    print("\n\n\n")
    exit(111)