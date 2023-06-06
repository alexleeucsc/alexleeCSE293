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
        self.signA = pyrtl.WireVector(1, 'signA'+nameTag)
        self.expA = pyrtl.WireVector(self.expLen, 'expA'+nameTag)
        self.manA = pyrtl.WireVector(self.manLen, 'manA'+nameTag)
        self.signB = pyrtl.WireVector(1, 'signB'+nameTag)
        self.expB = pyrtl.WireVector(self.expLen, 'expB'+nameTag)
        self.manB = pyrtl.WireVector(self.manLen, 'manB'+nameTag)
        self.signC = pyrtl.WireVector(1, 'signC'+nameTag)
        self.expC = pyrtl.WireVector(self.expLen, 'expC'+nameTag)
        self.manC = pyrtl.WireVector(self.manLen, 'manCFinal'+nameTag)
        #Wires
        #You'll probably find it easier to add intermediate wires. To orginize this class an as object, please add them here, with the format:
        #self.my_wire = pyrtl.WireVector(self.my_wire_len, 'my_wire'+nameTag)

    def addLogicFloat(self,float_A, float_B, float_C):
        #--------------------------------------------------
        #   YOUR CODE HERE
        #--------------------------------------------------
        return


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