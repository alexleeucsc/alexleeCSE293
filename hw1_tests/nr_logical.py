
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
#helpers:
def zeroExtendLeft(binStr, strLen):
    return '0'*(strLen-len(binStr)) + binStr
def zeroExtendRight(binStr, strLen):
    return binStr + '0'*(strLen-len(binStr))
def correctExpLen(binStr, strLen):
    if len(binStr)<=strLen:
        return zeroExtendLeft(binStr, strLen)
    else:
        return binStr[:strLen]
def correctMantLen(binStr, strLen):
    if len(binStr)<=strLen:
        return zeroExtendRight(binStr, strLen)
    else:
        return binStr[:strLen]

#3a: write a model to convert python floating point numbers to logical floating point representations
# bias = (2 << (8-1))
def logicFloat_to_float(logicFloat, expLen, manLen):
    signBit, expBits, manBits = logicFloat
    assert(len(manBits)==manLen)
    #assert(len(expBits)==expLen)
    if len(expBits)!=expLen:
        print(logicFloat)
        print(expBits, expLen)
        exit(111)
    bias = pow(2,expLen-1)
    # NOTE: as a side note; we NEED the expBits and manBits to be the right length coming in
    # if len(manBits)>manLen-1:
    #     print("\    return '0'*(strLen-len(binStr)) + binStr needed:", len(manBits))
    #     print('1'+zeroExtendLeft(manBits, manLen), "=>", int('1'+zeroExtendLeft(manBits, manLen),2))
    #     print('1'+manBits, "=>", int('1'+manBits,2))
    return (-1 if signBit=='1' else 1) * pow(2, int(expBits, 2)-bias) * int('1'+manBits,2) * pow(2,-manLen)
    #BUG 052123: zeroExtendLeft (works without if expBits and manBits are right len; make sure of that))
    #NOTE 052123: manBits are guranteed to be of the form
    #[1][.][00010101...1], where mantBits = '00010101...1' and is always mantBits long

def float_to_Logicfloat(floatIn, expLen, manLen):
    whole,frac = int(floatIn), floatIn - int(floatIn)
    mantWhole,mantFrac = bin(whole)[2:] if whole>0 else '', ''
    #exp = pow(2,expLen-1) #BUG 052023 - exp should start at bias!
    #while len(mantFrac)+len(mantWhole) < manLen+1 and exp>0  and frac != 0:
    while len(mantFrac)+len(mantWhole) < manLen+1 and frac != 0:
        frac = frac * 2
        mantFrac += ('1' if frac > 1 else '0')
        frac -= 1 if frac >= 1 else 0 #subtle bug: should be frac >= 1 not frac > 1
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
    #052123 NOTE:
    #mantWhole+mantFrac is guranteed to be a string with a 1 in front, so long as mantWhole>1
    #when mantWhole is 0, mantFrac is shifted left until the first digit is 1, and exp is increased
    #either way, mantWhole+mantFrac will ahve a 1 in front, which will be cut off by the [1:]
    return ['1' if floatIn<0 else '0', zeroExtendLeft(bin(exp)[2:], expLen), zeroExtendRight((mantWhole+mantFrac)[1:], manLen)]

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
    return [signBit, zeroExtendLeft(bin(exp)[2:], expLen), manBits]
#3c: write the multiplication function between floating points
#assume that expBits and manBits are the same length in A, B, and C
def multiplyLogicFloat(logicFloatA, logicFloatB, expLen, manLen):
    signBitA, expBitsA, manBitsA = logicFloatA
    signBitB, expBitsB, manBitsB = logicFloatB
    #get expBits and manBits
    expC = int(expBitsA, 2) + int(expBitsB, 2) - pow(2,expLen-1)
    # print("expC",expC)
    # print(bin(expC))
    # manC = int('1'+zeroExtendLeft(manBitsA, manLen), 2) * int('1'+zeroExtendLeft(manBitsB, manLen), 2)
    # manCScaled = int('1'+zeroExtendLeft(manBitsA, manLen), 2) * int('1'+zeroExtendLeft(manBitsB, manLen), 2) * pow(2,-1*(manLen)) * pow(2,-1*(manLen))
    manC = int('1'+manBitsA, 2) * int('1'+manBitsB, 2)
    manCScaled = int('1'+manBitsA, 2) * int('1'+manBitsB, 2) * pow(2,-1*(manLen)) * pow(2,-1*(manLen))
    #if mantisa overflow, shift until fits, then increase exp
    #note that manBitsA/manBitsB are at least 1.0, and are atmost 1.1111...1
    #1.0*1.0 is 1, and 1.111... * 1.111... = 1.999...*1.999... ~ 3.999...
    #so, manC should be between 1 and 3.999..._10 = 11.111..._2
    #clearly, the only case where we shift is if manC is bigger than or equal to 2.0:
    #also, note that each manBitsA/B comes in as a manLen-wide signal
    #...more instruction on this point here:
    assert(manCScaled>=1.0 and manCScaled<=4.0)
    manBitsC = bin(manC)[2:]
    # if len(manBitsC)==(manLen*2)+1:
    #     continue
    # else:
    #     assert(len(manBitsC)==(manLen*2)+2)
    #     expC += 1
    if len(manBitsC)==(manLen*2)+2:
        expC += 1
    else:
        assert(len(manBitsC)==(manLen*2)+1)
    manBitsC = manBitsC[:manLen+1]
    #finally, the multplier can overflow: write the code here to check for an overflow
    if expC >= pow(2,expLen):
        print("LOG: multiply overflow!")
    if expC < 0:
        print("LOG: multiply underflow!")
    signBitC = str(int(signBitA)^int(signBitB))
    return [signBitC, bin(expC)[2:], manBitsC[1:]]

#3d:  write the addition function between floating points
def addLogicFloat(logicFloatA, logicFloatB, expLen, manLen):
    signBitA, expBitsA, manBitsA = logicFloatA
    signBitB, expBitsB, manBitsB = logicFloatB
    #1: compare exp, keep bigger exp, then shiftright the mantissa of the smaller one
    if int(expBitsA,2) > int(expBitsB,2):
        expBitsC = expBitsA
        shiftRightAmount = int(expBitsA,2) - int(expBitsB,2)
        manBitsB = '0'*(manLen-shiftRightAmount-1) + '1' + manBitsB[shiftRightAmount:]
        manBitsA = '0'*(manLen-len(manBitsA)-1) + '1' + manBitsA
    else:
        expBitsC = expBitsB
        shiftRightAmount = int(expBitsB,2) - int(expBitsA,2)
        manBitsA = '0'*(manLen-shiftRightAmount-1) + '1' + manBitsA[shiftRightAmount:]
        manBitsB = '0'*(manLen-len(manBitsA)-1) + '1' + manBitsB
    #2: add mantissas: if overflow, shift mantissa to right one bit
    manC = (-1 if signBitA=='1' else 1)*int(manBitsA,2) + (-1 if signBitB=='1' else 1)*int(manBitsB,2)
    #2b: if mantissa neg, turn pos and set sign bit
    if manC<0:
        signBitC = 1
        manC = manC * -1
    else:
        signBitC = 0
    #2d: set mantissa bits for C
    manBitsC = correctMantLen( bin(manC)[2:], manLen+1 )
    # if len(manBitsC)==manLen+2:
    #     #print("shifted")
    #     #print(manBitsC, '0'+manBitsC[:-1])
    #     manBitsC = '0'+manBitsC[:-1]
    # else:
    #     if len(manBitsC)!=manLen+1:
    #         print("mantLen error")
    #         print(manBitsC,manLen)
    #         exit(111)
    if manC > (pow(2,manLen+1)-1):
        expBitsC = correctExpLen( bin(int(expBitsC, 2)+1)[2:], expLen )
    #print("debug:")
    #print(signBitC, expBitsC, manBitsC[1:])
    return [signBitC, expBitsC, manBitsC[1:]]

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

