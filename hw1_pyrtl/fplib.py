import pyrtl

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

