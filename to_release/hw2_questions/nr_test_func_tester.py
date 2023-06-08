from pyrtl import *
from fplib import *
from math import pow
import random
from providedLib import prioritized_mux
from adder_class import *
from mult_class import *
from shifter_class import *

pyrtl.reset_working_block()

#params
expLen = 8
manLen = 16
max_iter = 10
# state enums
WAITING, MULTIPLYING, DONE = [pyrtl.Const(x, bitwidth=2) for x in range(3)]

#inputs
float_A = pyrtl.Input(expLen+manLen+1, 'float_A')
float_B = pyrtl.Input(expLen+manLen+1, 'float_B')
valid_ab = pyrtl.Input(1, 'valid_ab')
ready_c = pyrtl.Input(1, 'ready_c')
#outputs
float_C = pyrtl.Output(expLen+manLen+1, 'float_C')
valid_c = pyrtl.Output(1, 'valid_c')
ready_ab = pyrtl.Output(1, 'ready_ab')

#BEGIN CIRCUIT ASSIGNMENTS
#state
state = pyrtl.Register(3, 'state')

#Wires
#You'll probably find it easier to add intermediate wires. To orginize this class an as object, please add them here, with the format:
#self.my_wire = pyrtl.WireVector(self.my_wire_len, 'my_wire'+nameTag)

with pyrtl.conditional_assignment as condAssignObj:
    #--------------------------------------------------
    #   YOUR CODE HERE
    #--------------------------------------------------

sim_trace = pyrtl.SimulationTrace()
sim = pyrtl.Simulation(tracer=sim_trace, register_value_map={})

def binWireToFloat(wireToInspect, wireWidth):
    wireToInspect_int = sim.inspect(wireToInspect)
    wireToInspect_str = zeroExtendLeft(bin(wireToInspect_int)[2:], wireWidth)
    print("\t\twirelogical",[wireToInspect_str[0], wireToInspect_str[1:expLen+1], wireToInspect_str[expLen+1:]])
    wireToInspect_val = logicFloat_to_float([wireToInspect_str[0], wireToInspect_str[1:expLen+1], wireToInspect_str[expLen+1:]], expLen, manLen)
    return wireToInspect_val

for cycle in range(100):
    print("---------- NEW DIV Q"+str(cycle)+" ----------")
    rand_flt_a = random.uniform(1,pow(2,5))
    rand_flt_b = random.uniform(1,pow(2,5))
    a_sign = random.choice([1,-1])
    b_sign = random.choice([1,-1])
    rand_flt_a = rand_flt_a * a_sign
    rand_flt_b = rand_flt_b * b_sign
    print("rand_flt_a",rand_flt_a)
    print("rand_flt_b",rand_flt_b)
    logicValA = float_to_Logicfloat(rand_flt_a,expLen,manLen)
    logicValB = float_to_Logicfloat(rand_flt_b,expLen,manLen)
    print("logicValA",logicValA)
    print("logicValB",logicValB)
    strValA = ''.join(logicValA)
    strValB = ''.join(logicValB)
    #--------------------------------------------------
    #   YOUR CODE HERE
    #--------------------------------------------------

