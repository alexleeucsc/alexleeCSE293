
import math
import random
#part 1 logical mdoels: multiplier
#the point of this part is to write a logical model for multiplicaiton

#part 2 logical models
#the formula for this are taken from the wikipedia entry:
#@https://en.wikipedia.org/wiki/Division_algorithm#Newton%E2%80%93Raphson_division
def nr_logical(num,div,rep=10):
    e = (pow(2,int(math.log(div,2)+1)))
    print("pow of 2 normalizing factor:", e)
    num = num / e
    div = div / e
    print(div)
    rec_guess = (48/17)-(32/17)*div
    for _ in range(rep):
        print("new guess for reciprocol:",rec_guess)
        rec_guess = rec_guess + rec_guess*(1-(div*rec_guess))
    return num*rec_guess
#print(nr_logical(121,11))

#part 3 logical models w/ floating point representaiton
#3a: write a model to convert python floating point numbers to logical floating point representations
# bias = (2 << (8-1))
def logicFloat_to_float(logicFloat, expLen, manLen):
    signBit, expBits, manBits = logicFloat
    bias = pow(2,expLen-1)
    return (-1 if signBit=='1' else 1) * pow(2, int(expBits, 2)-bias) * int('1'+manBits,2) * pow(2,-manLen)
def float_to_Logicfloat(floatIn, expLen, manLen):
    whole,frac = int(floatIn), floatIn - int(floatIn)
    mantWhole,mantFrac = bin(whole)[2:] if whole>0 else '', ''
    #exp = pow(2,expLen-1) #BUG 052023 - exp should start at bias!
    #while len(mantFrac)+len(mantWhole) < manLen+1 and exp>0  and frac != 0:
    while len(mantFrac)+len(mantWhole) < manLen+1 and frac != 0:
        frac = frac * 2
        mantFrac += ('1' if frac > 1 else '0')
        frac -= 1 if frac > 1 else 0
        #print(exp, bin(exp))
    if (whole==0 and all([digit=='0' for digit in mantFrac])):
        print("zero not supported yet")
        raise ValueError("zero not supported yet")
    if whole>0:
        exp = len(bin(whole)[2:])-1
    else:
        exp = (-1*mantFrac.index('1'))-1
    exp = exp + pow(2,expLen-1)
    assert(mantWhole=='' or mantWhole[0]=='1')
    return ['1' if floatIn<0 else '0', bin(exp)[2:], (mantWhole+mantFrac)[1:]]

#3b: write the bitshift function between floating points
#this function should only shift a floating point number LEFT, or division w/ a pwoer of 2
#the logic should subtract from the mantisa UNTIL 
def shiftRightLogicFloat(logicFloat, expLen,manLen, shiftLeftAmount):
    signBit, expBits, manBits = logicFloat
    exp = int(expBits,2)
    if exp>=shiftLeftAmount:
        exp -= shiftLeftAmount
    else:
        exp = 0
        print("LOG: shifted left until 0!")
    return [signBit, bin(exp)[2:], manBits]
#3c: write the multiplication function between floating points

#3d:  write the addition function between floating points

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
print("t1:")
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
print("t2:")
for _2 in range(2000):
    expWidth = random.randint(8,30)
    manWidth = random.randint(8,30)
    for _ in range(10000):
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
def nr_logical(num,div,rep=10):
    e = (pow(2,int(math.log(div,2)+1)))
    print("pow of 2 normalizing factor:", e)
    num = num / e
    div = div / e
    print(div)
    rec_guess = (48/17)-(32/17)*div
    for _ in range(rep):
        print("new guess for reciprocol:",rec_guess)
        rec_guess = rec_guess + rec_guess*(1-(div*rec_guess))
    return num*rec_guess
#print(nr_logical(121,11))

