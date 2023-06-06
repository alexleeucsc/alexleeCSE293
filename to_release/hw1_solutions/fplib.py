import pyrtl
import random

class pyrtl_float:
    def __init__(self, signBit, expBits, mantBits, expLen, D):
        self.signBit = signBit
        self.expBits = expBits
        self.mantBits = mantBits
        self.expLen = expLen
        self.mantLen = mantLen
        assert(len(expBits) == expLen)
        assert(len(mantBits) == mantLen)


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

def logicFloat_to_float(logicFloat, expLen, manLen):
    signBit, expBits, manBits = logicFloat
    assert(len(manBits)==manLen)
    if len(expBits)!=expLen:
        print(logicFloat)
        print(expBits, expLen)
        exit(111)
    bias = pow(2,expLen-1)
    return (-1 if signBit=='1' else 1) * pow(2, int(expBits, 2)-bias) * int('1'+manBits,2) * pow(2,-manLen)

def float_to_Logicfloat(floatIn, expLen, manLen):
    if floatIn<0:
        floatIn = floatIn * -1
        signBit = '1'
    else:
        signBit = '0'
    whole,frac = int(floatIn), floatIn - int(floatIn)
    mantWhole,mantFrac = bin(whole)[2:] if whole>0 else '', ''
    while len(mantFrac)+len(mantWhole) < manLen+1 and frac != 0:
        frac = frac * 2
        mantFrac += ('1' if frac > 1 else '0')
        frac -= 1 if frac >= 1 else 0 #subtle bug: should be frac >= 1 not frac > 1
    if (whole==0 and all([digit=='0' for digit in mantFrac])):
        print("zero not supported yet")
        raise ValueError("zero not supported yet")
    mantConcat = (mantWhole+mantFrac)
    if whole>0:
        exp = len(bin(whole)[2:])-1
    else:
        exp = (-1*mantFrac.index('1'))-1
        mantConcat = (mantWhole+mantFrac)[mantFrac.index('1'):]
    exp = exp + pow(2,expLen-1)
    assert(mantWhole=='' or mantWhole[0]=='1')
    return [signBit, zeroExtendLeft(bin(exp)[2:], expLen), zeroExtendRight((mantConcat)[1:], manLen)]

if __name__ == "__main__":
    for _ in range(10000):
        rand_flt_a = random.uniform(0.001,pow(2,5))
        a_sign = random.choice([1,-1])
        rand_flt_a = rand_flt_a * a_sign
        rand_flt_proc = logicFloat_to_float(float_to_Logicfloat(rand_flt_a, 8, 64), 8, 64)
        assert(abs(rand_flt_a - rand_flt_proc) < 0.1)