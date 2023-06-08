from pyrtl import *
from fplib import *
from math import pow
import random
from providedLib import prioritized_mux

pyrtl.reset_working_block()

#params
expLen = 8
manLen = 16
#inputs
float_A = pyrtl.Input(expLen+manLen+1, 'float_A')
float_B = pyrtl.Input(expLen+manLen+1, 'float_B')
#outputs
float_C = pyrtl.Output(expLen+manLen+1, 'float_C')

class addTestClass:
    def __init__(self,nameTag,expLen,manLen):
        self.expLen = 8
        self.manLen = 16
        #wires
        # self.signA = pyrtl.WireVector(1, 'signA'+nameTag)
        # self.expA = pyrtl.WireVector(self.expLen, 'expA'+nameTag)
        # self.manA = pyrtl.WireVector(self.manLen, 'manA'+nameTag)
        # self.signB = pyrtl.WireVector(1, 'signB'+nameTag)
        #self.expB = pyrtl.WireVector(self.expLen, 'expB'+nameTag)
        # self.manB = pyrtl.WireVector(self.manLen, 'manB'+nameTag)
        self.signC = pyrtl.WireVector(1, 'signC'+nameTag)
        self.expC = pyrtl.WireVector(self.expLen, 'expC'+nameTag)
        self.manC = pyrtl.WireVector(self.manLen, 'manCFinal'+nameTag)
        #Wires
        self.manBitsAFix = pyrtl.WireVector(self.manLen+1, 'manBitsAFix'+nameTag)
        self.manBitsBFix = pyrtl.WireVector(self.manLen+1, 'manBitsBFix'+nameTag)
        self.shiftRightAmount = pyrtl.WireVector(self.expLen+1, 'shiftRightAmount'+nameTag)
        self.manBitsAFixSign = pyrtl.WireVector(self.manLen+3, 'manBitsAFixSign'+nameTag)
        self.manBitsBFixSign = pyrtl.WireVector(self.manLen+3, 'manBitsBFixSign'+nameTag)
        self.manCExt = pyrtl.WireVector(self.manLen+3, 'manCExt'+nameTag)
        self.manCFixExt = pyrtl.WireVector(self.manLen+2, 'manCFixExt'+nameTag)
        self.expCMid = pyrtl.WireVector(self.expLen, 'expCMid'+nameTag)
        self.fisrtOneIdxManC = pyrtl.WireVector(256, 'fisrtOneIdx'+nameTag)
        #debug wires
        self.manCExtDebug = pyrtl.WireVector(self.manLen+2, 'manCExtDebug'+nameTag)
        self.manCFixExtDebug = pyrtl.WireVector(self.manLen+1, 'manCFixExtDebug'+nameTag)
        #abCompareDebug = pyrtl.WireVector(1, 'abCompareDebug')
    def addLogicFloat(self,float_A, float_B, float_C):
        self.signA = float_A[self.expLen+self.manLen]
        self.expA = float_A[self.manLen:self.expLen+self.manLen]
        self.manA = float_A[:self.manLen]
        self.signB = float_B[self.expLen+self.manLen]
        self.expB = float_B[self.manLen:self.expLen+self.manLen]
        self.manB = float_B[:self.manLen]

        self.expCMid <<= select((self.expA >= self.expB), self.expA, self.expB)
        self.shiftRightAmount <<= select((self.expA >= self.expB), self.expA + ~self.expB + 1 - pyrtl.Const(str(self.expLen+1)+"'b1"+("0"*(self.expLen))), self.expB + ~self.expA + 1 - pyrtl.Const(str(self.expLen+1)+"'b1"+("0"*(self.expLen))))
        self.manBitsBFix <<= select((self.expA >= self.expB), pyrtl.shift_right_logical(pyrtl.concat(pyrtl.Const("1'b1"), self.manB), self.shiftRightAmount), pyrtl.concat(pyrtl.Const("1'b1"), self.manB))
        self.manBitsAFix <<= select((self.expA >= self.expB), pyrtl.concat(pyrtl.Const("1'b1"), self.manA), pyrtl.shift_right_logical(pyrtl.concat(pyrtl.Const("1'b1"), self.manA), self.shiftRightAmount))

        self.manBitsAFixSign <<= select(self.signA==pyrtl.Const("1'b1"), pyrtl.concat(pyrtl.Const("2'b11"), (~self.manBitsAFix + 1)[:self.manLen+1]), self.manBitsAFix)

        self.manBitsBFixSign <<= select(self.signB==pyrtl.Const("1'b1"), pyrtl.concat(pyrtl.Const("2'b11"), (~self.manBitsBFix + 1)[:self.manLen+1]), self.manBitsBFix)
        self.manCExt <<= self.manBitsAFixSign + self.manBitsBFixSign
        self.manCExtDebug <<= self.manCExt

        self.signC <<= select(self.manCExt[-1] == pyrtl.Const("1'b1"), pyrtl.Const("1'b1"), pyrtl.Const("1'b0"))
        self.manCFixExt <<= select(self.manCExt[-1] == pyrtl.Const("1'b1"), ~self.manCExt[:self.manLen+2] + 1, self.manCExt[:self.manLen+2])
        self.manCFixExtDebug <<= self.manCFixExt

        vals = [Const(i) for i in range(self.manLen+2)]
        self.fisrtOneIdxManC <<= select(self.manCFixExt[-1] == pyrtl.Const("1'b1"), pyrtl.Const(1), prioritized_mux(self.manCFixExt, vals))
        self.expC <<= select(self.manCFixExt[-1] == pyrtl.Const("1'b1"), self.expCMid+1, self.expCMid - (self.manLen-self.fisrtOneIdxManC))
        self.manC <<= select(self.manCFixExt[-1] == pyrtl.Const("1'b1"), self.manCFixExt[1:self.manLen+1], pyrtl.shift_left_logical(self.manCFixExt, self.manLen-self.fisrtOneIdxManC))

        float_C <<= pyrtl.concat_list([self.manC, self.expC, self.signC])


if __name__ == "__main__":
    addTestObj = addTestClass("obj1", expLen,manLen)
    addTestObj.addLogicFloat(float_A, float_B, float_C)
    sim_trace = pyrtl.SimulationTrace()
    sim = pyrtl.Simulation(tracer=sim_trace, register_value_map={})
    for cycle in range(10000):
        rand_flt_a = random.uniform(0.001,pow(2,5))
        rand_flt_b = random.uniform(0.001,pow(2,5))
        a_sign = random.choice([1,-1])
        b_sign = random.choice([1,-1])
        rand_flt_a = rand_flt_a * a_sign
        rand_flt_b = rand_flt_b * b_sign
        print("rand_flt_a",rand_flt_a)
        print("rand_flt_b",rand_flt_b)
        logicValA = float_to_Logicfloat(rand_flt_a,expLen,manLen)
        logicValB = float_to_Logicfloat(rand_flt_b,expLen,manLen)
        strValA = ''.join(logicValA)
        strValB = ''.join(logicValB)
        sim.step({
            'float_A': int(strValA, 2),
            'float_B': int(strValB, 2),
        })
        float_C_val_int = sim.inspect(float_C)
        float_C_val_str = zeroExtendLeft(bin(float_C_val_int)[2:], expLen+manLen+1)
        float_C_val = logicFloat_to_float([float_C_val_str[0], float_C_val_str[1:expLen+1], float_C_val_str[expLen+1:]], expLen, manLen)
        pyOut = rand_flt_a + rand_flt_b
        print("float_C_val", float_C_val, "vs expected:", pyOut)
        print("\n")
        assert(abs(float_C_val-pyOut)<1)


    print('--- Simulation ---')
    sim_trace.render_trace(symbol_len=5, segment_size=5)

    c_value = sim.inspect(float_C)
    print("The latest value of 'c' was: " + str(c_value))