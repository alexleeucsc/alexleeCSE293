import pyrtl
import random
import math
from fplib import *
from math import pow
pyrtl.reset_working_block()

#params
expLen = 8
manLen = 32
#inputs
float_A = pyrtl.Input(expLen+manLen+1, 'float_A')
shiftLeftAmount = pyrtl.Input(64, 'shiftLeftAmount')
#outputs
float_C = pyrtl.Output(expLen+manLen+1, 'float_C')

class shiftTestClass:
    def __init__(self,nameTag,expLen,manLen):
        self.expLen = expLen
        self.manLen = manLen
        #wires
        self.signA = pyrtl.WireVector(1, 'signA'+nameTag)
        self.expA = pyrtl.WireVector(self.expLen, 'expA'+nameTag)
        self.manA = pyrtl.WireVector(self.manLen, 'manA'+nameTag)
        #Wires
        #You'll probably find it easier to add intermediate wires. To orginize this class an as object, please add them here, with the format:
        #self.my_wire = pyrtl.WireVector(self.my_wire_len, 'my_wire'+nameTag)
    def shiftRightLogicFloat(self, float_A, float_C, shiftLeftAmount):
        #--------------------------------------------------
        #   YOUR CODE HERE
        #--------------------------------------------------
        return



if __name__ == "__main__":
    shiftTestObj = shiftTestClass("obj1", expLen,manLen)
    shiftTestObj.shiftRightLogicFloat(float_A, float_C, shiftLeftAmount)
    sim_trace = pyrtl.SimulationTrace()
    sim = pyrtl.Simulation(tracer=sim_trace, register_value_map={})
    for cycle in range(1000):
        rand_flt_a = random.uniform(1,pow(2,5))
        shiftLeftAmount = random.randint(0,int(math.log2(rand_flt_a)))
        a_sign = random.choice([1,-1])
        rand_flt_a = rand_flt_a * a_sign
        print("rand_flt_a",rand_flt_a)
        print("shiftLeftAmount",shiftLeftAmount)
        logicVal1 = float_to_Logicfloat(rand_flt_a,expLen,manLen)
        strVal1 = ''.join(logicVal1)
        sim.step({
            'float_A': int(strVal1, 2),
            'shiftLeftAmount': shiftLeftAmount,
        })
        float_C_val_int = sim.inspect(float_C)
        float_C_val_str = zeroExtendLeft(bin(float_C_val_int)[2:], expLen+manLen+1)
        float_C_val = logicFloat_to_float([float_C_val_str[0], float_C_val_str[1:expLen+1], float_C_val_str[expLen+1:]], expLen, manLen)
        pyOut = rand_flt_a / pow(2,shiftLeftAmount)
        print("float_C_val", float_C_val, "vs expected:", pyOut)
        assert(abs(float_C_val-pyOut)<1)
    print('--- Simulation ---')
    sim_trace.render_trace(symbol_len=5, segment_size=5)