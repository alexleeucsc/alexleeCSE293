from nr_logical import *
#test logicFloat_to_float and float_to_Logicfloat
rand_flt, expWidth, manWidth = 56.87, 8, 64

expWidth = random.randint(3,30)
manWidth = random.randint(3,30)
rand_flt = random.uniform(0,pow(2,manWidth))
#bug 1: the random float has to fit entirely in the mantisa:
#otherwise, it will be off by a large number
shiftLeftAmount = 5
logicFloat = float_to_Logicfloat(rand_flt, expWidth, manWidth)
print(logicFloat)
floatOut = logicFloat_to_float(logicFloat, expWidth, manWidth)
print(floatOut)
assert(abs(rand_flt-floatOut)<1.5)
print("t1: logical to python")
for _2 in range(500):
    expWidth = random.randint(8,30)
    manWidth = random.randint(8,30)
    for _ in range(1000):
        rand_flt = random.uniform(0,pow(2,manWidth))
        if rand_flt==0:
            print("oops, zero")
            continue
        logicFloat = float_to_Logicfloat(rand_flt, expWidth, manWidth)
        floatOut = logicFloat_to_float(logicFloat, expWidth, manWidth)
        if(abs(rand_flt-floatOut)>2):
            print("errro:")
            print(expWidth, manWidth)
            print(logicFloat)
            print(rand_flt,floatOut)
            exit(111)
        # else:
        #     print("ok")
        #     print(expWidth, manWidth)
        #     print(logicFloat)
        #     print(rand_flt,floatOut)
#test leftshift
print("t2: leftshift")
for _2 in range(500):
    expWidth = random.randint(8,30)
    manWidth = random.randint(8,30)
    for _ in range(1000):
        shiftLeftAmount = random.randint(3,expWidth)
        rand_flt = random.uniform(0.001,pow(2,manWidth))
        if rand_flt < pow(2,-1*expWidth/2):
            print("currently doesn't support zero")
            continue
        #Bug 2: if rand+flt is REALLY small, then expWidth must be big enough to capture it
        #if 2^-(expWidth-1) is bigger than rand_flt, then rand_flt will be represented by a zero
        #NOTE: the bug that this causes is weird: it causes the mantisa to not find the '1' in string
        #...since this is rare we will deal with it later
        if rand_flt < pow(2,-1*manWidth):
            print("currently doesn't support zero")
            continue
        if rand_flt==0:
            print("oops, zero")
            continue
        try:
            logicFloat = float_to_Logicfloat(rand_flt, expWidth, manWidth)
        except ValueError:
            print("ValueError")
            print(expWidth, manWidth)
            print(rand_flt)
            exit(111)
        logicFloatPrime = shiftRightLogicFloat(logicFloat, expWidth, manWidth, shiftLeftAmount)
        floatOut = logicFloat_to_float(logicFloatPrime, expWidth, manWidth)
        rand_fltPrime = rand_flt/pow(2,shiftLeftAmount)
        if(abs(rand_fltPrime-floatOut)>2):
            print("errro:")
            print(expWidth, manWidth)
            print(logicFloat)
            print(rand_flt,floatOut)
            exit(111)
        # else:
        #     print("ok")
        #     print(expWidth, manWidth)
        #     print(logicFloat)
        #     print(rand_flt,floatOut)
#test leftshift
print("t3: mult")
for _2 in range(500):
    expWidth = random.randint(8,30)
    manWidth = random.randint(8,30)
    for _ in range(1000):
        shiftLeftAmount = random.randint(3,expWidth)
        rand_flt = random.uniform(0.001,pow(2,manWidth))
        if rand_flt < pow(2,-1*expWidth/2):
            print("currently doesn't support zero")
            continue
        #Bug 2: if rand+flt is REALLY small, then expWidth must be big enough to capture it
        #if 2^-(expWidth-1) is bigger than rand_flt, then rand_flt will be represented by a zero
        #NOTE: the bug that this causes is weird: it causes the mantisa to not find the '1' in string
        #...since this is rare we will deal with it later
        if rand_flt < pow(2,-1*manWidth):
            print("currently doesn't support zero")
            continue
        if rand_flt==0:
            print("oops, zero")
            continue
        try:
            logicFloat = float_to_Logicfloat(rand_flt, expWidth, manWidth)
        except ValueError:
            print("ValueError")
            print(expWidth, manWidth)
            print(rand_flt)
            exit(111)
        logicFloatPrime = shiftRightLogicFloat(logicFloat, expWidth, manWidth, shiftLeftAmount)
        floatOut = logicFloat_to_float(logicFloatPrime, expWidth, manWidth)
        rand_fltPrime = rand_flt/pow(2,shiftLeftAmount)
        if(abs(rand_fltPrime-floatOut)>2):
            print("errro:")
            print(expWidth, manWidth)
            print(logicFloat)
            print(rand_flt,floatOut)
            exit(111)
        # else:
        #     print("ok")
        #     print(expWidth, manWidth)
        #     print(logicFloat)
        #     print(rand_flt,floatOut)