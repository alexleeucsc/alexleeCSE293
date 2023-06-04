import pyrtl
import random
import math
from fplib import *
from math import pow
pyrtl.reset_working_block()

#params
expLen = 8
manLen = 32

# state enums
WAITING, MULTIPLYING = [pyrtl.Const(x, bitwidth=2) for x in range(2)]

#shifter is comb only; no regs

#inputs
float_A = pyrtl.Input(expLen+manLen+1, 'float_A')
shiftLeftAmount = pyrtl.Input(64, 'shiftLeftAmount')
#outputs
float_C = pyrtl.Output(expLen+manLen+1, 'float_C')

def shiftRightLogicFloat(float_A, float_C, shiftLeftAmount):
    #wires
    signA = pyrtl.WireVector(1, 'signA')
    expA = pyrtl.WireVector(expLen, 'expA')
    manA = pyrtl.WireVector(manLen, 'manA')
    manAFixWire = pyrtl.WireVector(manLen+1, 'manAFixWire')
    signA <<= float_A[0]
    expA <<= float_A[1:expLen+1]
    manA <<= float_A[expLen+1:]
    #concat 1 on left (msb) of manA
    manAFixWire <<= pyrtl.concat(manA, pyrtl.Const("1'b1"))
    with pyrtl.conditional_assignment:
        with expA>=shiftLeftAmount:
            #expA = expA - shiftLeftAmount
            float_C |= pyrtl.concat_list([manA, expA-shiftLeftAmount, signA]) #BUG 05/23/23: this list was flipped: however, the output of float_C wasn't just the bits flipped! Why is that? (TO DO!))
            #float_C |= pyrtl.concat_list([signA, expA, manA])
        with expA<shiftLeftAmount:
            #if you shift left until exp exits bounds, shoudl just go to zero
            #haven't handled 0 yet... fill in
            float_C |= pyrtl.concat_list([pyrtl.Const("1'b1"), pyrtl.Const("8'b11111111"), pyrtl.Const("32'b"+('1'*32))])


shiftRightLogicFloat(float_A, float_C, shiftLeftAmount)


#sim_trace = pyrtl.SimulationTrace(register_value_map={digitMask: "6'b111111"})
sim_trace = pyrtl.SimulationTrace()
#bug 051523: https://pyrtl.readthedocs.io/en/latest/simtest.html
# register_value_map has format {reg:int}
sim = pyrtl.Simulation(tracer=sim_trace, register_value_map={   })

#debugging specific functions

if __name__ == "__main__":
    for cycle in range(1000):
        rand_flt_a = random.uniform(1,pow(2,5))
        shiftLeftAmount = random.randint(0,int(math.log2(rand_flt_a)))
        logicVal1 = float_to_Logicfloat(rand_flt_a,expLen,manLen)
        strVal1 = ''.join(reversed(logicVal1))
        sim.step({
            'float_A': int(strVal1, 2),
            'shiftLeftAmount': shiftLeftAmount,
        })
        float_C_val_int = sim.inspect(float_C)
        print(float_C_val_int)
        print(bin(float_C_val_int)[2:])
        float_C_val_str = zeroExtendLeft(bin(float_C_val_int)[2:], expLen+manLen+1)
        float_C_val = logicFloat_to_float([float_C_val_str[0], float_C_val_str[1:expLen+1], float_C_val_str[expLen+1:]], expLen, manLen)
        print("The latest value of 'float_C_val' was: " + str(float_C_val))
        # print("\tvalue of 'signA' was: " + str(sim.inspect(signA)))
        # print("\tvalu of 'expA' was: " + str(bin(sim.inspect(expA))))
        # print("\tvalu of 'manA' was: " + str(bin(sim.inspect(manA))))
        print("logfloat rep C:",[float_C_val_str[0], float_C_val_str[1:expLen+1], float_C_val_str[expLen+1:]])
        print("logfloat rep input:",logicVal1)
        pyOut = rand_flt_a / pow(2,shiftLeftAmount)

    print('--- Simulation ---')
    sim_trace.render_trace(symbol_len=5, segment_size=5)

    # manA_val = sim.inspect(manA)
    # print("The latest value of 'c' was: " + str(manA_val))