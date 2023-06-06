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
    #--------------------------------------------------
    #   YOUR CODE HERE
    #--------------------------------------------------
    return

def float_to_Logicfloat(floatIn, expLen, manLen):
    #--------------------------------------------------
    #   YOUR CODE HERE
    #--------------------------------------------------
    return

if __name__ == "__main__":
    for _ in range(10000):
        rand_flt_a = random.uniform(0.001,pow(2,5))
        a_sign = random.choice([1,-1])
        rand_flt_a = rand_flt_a * a_sign
        rand_flt_proc = logicFloat_to_float(float_to_Logicfloat(rand_flt_a, 8, 64), 8, 64)
        assert(abs(rand_flt_a - rand_flt_proc) < 0.1)