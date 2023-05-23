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

testFloatRep = 0
testShift = 0
testMult = 0
testAdd = 1

if testFloatRep:
    print("t1: logical to python")
    for _2 in range(10):
        expWidth = random.randint(8,30)
        manWidth = random.randint(8,30)
        for _ in range(100):
            rand_flt = random.uniform(0,pow(2,manWidth))
            if rand_flt==0:
                print("oops, zero")
                continue
            logicFloat = float_to_Logicfloat(rand_flt, expWidth, manWidth)
            floatOut = logicFloat_to_float(logicFloat, expWidth, manWidth)
            if(abs(rand_flt-floatOut)>2):
                print("rep not acc:")
                print(expWidth, manWidth)
                print(logicFloat)
                print(rand_flt,floatOut)
                exit(111)
            else:
                print("rep fine:")
                print(expWidth, manWidth)
                print(logicFloat)
                print(rand_flt,floatOut)           
            logicFloatCutoff = float_to_Logicfloat(floatOut, expWidth, manWidth)
            floatOutCutOff = logicFloat_to_float(logicFloatCutoff, expWidth, manWidth)
            if(abs(floatOut-floatOutCutOff)>0.2):
                print("cutoff rep not acc:")
                print(floatOut, floatOutCutOff, abs(floatOut-floatOutCutOff))
                print(logicFloatCutoff)
                exit(111)
            else:
                print("cutoff rep fine:")
                print(floatOut, floatOutCutOff)
                print(logicFloatCutoff)
    #test leftshift
if testShift:
    print("t2: leftshift")
    for _2 in range(10):
        expWidth = random.randint(8,30)
        manWidth = random.randint(8,30)
        for _ in range(100):
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
                print("shift err:")
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
if testMult:
    print("t3: mult")
    for _2 in range(5):
        expWidth = random.randint(8,30)
        manWidth = random.randint(8,30)
        for _ in range(5):
            rand_flt_a = random.uniform(0.001,pow(2,manWidth))
            rand_flt_b = random.uniform(0.001,pow(2,manWidth))
            # rand_flt_a = random.uniform(0.001,min(5,pow(2,manWidth)))
            # rand_flt_b = random.uniform(0.001,min(5,pow(2,manWidth)))
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
                logicFloatA = float_to_Logicfloat(rand_flt_a, expWidth, manWidth)
                logicFloatB = float_to_Logicfloat(rand_flt_b, expWidth, manWidth)
            #how accurate should we expect the output to be?
            #
            except ValueError:
                print("ValueError")
                print(expWidth, manWidth)
                print(rand_flt)
                exit(111)
            logicFloatPrime = multiplyLogicFloat(logicFloatA, logicFloatB, expWidth, manWidth)
            floatOut = logicFloat_to_float(logicFloatPrime, expWidth, manWidth)
            rand_fltPrime = rand_flt_a*rand_flt_b
            if(abs(rand_fltPrime-floatOut)>(rand_fltPrime/2)):
                print("mult err:")
                print(rand_flt_a, rand_flt_b)
                print(logicFloatA, logicFloatB)
                print(logicFloatPrime)
                print(rand_fltPrime,floatOut)                
            # else:
            #     print("ok")
            #     print(rand_flt_a, rand_flt_b)
            #     print(logicFloatA, logicFloatB)
            #     print(logicFloatPrime)
            #     print(rand_fltPrime,floatOut)
#test addition
if testAdd:
    print("t4: add")
    for _2 in range(1000):
        expWidth = random.randint(8,30)
        manWidth = random.randint(8,30)
        for _ in range(10000):
            rand_flt_a = random.uniform(0.001,pow(2,manWidth))
            rand_flt_b = random.uniform(0.001,pow(2,manWidth))
            # rand_flt_a = random.uniform(0.001,min(5,pow(2,manWidth)))
            # rand_flt_b = random.uniform(0.001,min(5,pow(2,manWidth)))
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
                logicFloatA = float_to_Logicfloat(rand_flt_a, expWidth, manWidth)
                logicFloatB = float_to_Logicfloat(rand_flt_b, expWidth, manWidth)
            #how accurate should we expect the output to be?
            #
            except ValueError:
                print("ValueError")
                print(expWidth, manWidth)
                print(rand_flt_a)
                print(rand_flt_b)
                #exit(111)
            logicFloatPrime = addLogicFloat(logicFloatA, logicFloatB, expWidth, manWidth)
            floatOut = logicFloat_to_float(logicFloatPrime, expWidth, manWidth)
            rand_fltPrime = rand_flt_a+rand_flt_b
            if(abs(rand_fltPrime-floatOut)>(rand_fltPrime/2)):
                print("add err:")
                print(rand_flt_a, rand_flt_b)
                print(logicFloatA, logicFloatB)
                print(logicFloatPrime)
                print(rand_fltPrime,floatOut)                
            # else:
            #     print("ok")
            #     print(rand_flt_a, rand_flt_b)
            #     print(logicFloatA, logicFloatB)
            #     print(logicFloatPrime)
            #     print(rand_fltPrime,floatOut)
    print("passed")