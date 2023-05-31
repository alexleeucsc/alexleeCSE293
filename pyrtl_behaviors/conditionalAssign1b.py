from pyrtl import *
from fplib import *
from math import pow
import random
reset_working_block()

#params
expLen = 8
manLen = 16

# state enums
WAITING, MULTIPLYING = [Const(x, bitwidth=2) for x in range(2)]


# ready_ab_reg = Register(1, 'ready_ab_reg')
# valid_c_reg = Register(1, 'valid_c_reg')
# mult_state = Register(1, 'mult_state')

#inputs
float_A = Input(expLen+manLen+1, 'float_A')
float_B = Input(expLen+manLen+1, 'float_B')
expA = WireVector(expLen, 'expA')
expB = WireVector(expLen, 'expB')

expA <<= float_A[1:expLen]
expB <<= float_B[1:expLen]
abCompareDebug = WireVector(1, 'abCompareDebug')

with conditional_assignment:
    #1: compare exp, keep bigger exp, then shiftright the mantissa of the smaller one
    abCompareDebug <<= (expA > expB)
    with expA > expB:
        shiftRightAmountRev = Const("5'b11001")
    with expA < expB:
        shiftRightAmountRev = Const("5'b10101")

sim_trace = SimulationTrace()
sim = Simulation(tracer=sim_trace, register_value_map={})


for cycle in range(1):
    rand_flt_a = 27.975501666579657
    rand_flt_b = 5.791934863334932
    # print("rand_flt_a",rand_flt_a)
    # print("rand_flt_b",rand_flt_b)
    logicValA = float_to_Logicfloat(rand_flt_a,expLen,manLen)
    logicValB = float_to_Logicfloat(rand_flt_b,expLen,manLen)
    strValA = ''.join(reversed(logicValA))
    strValB = ''.join(reversed(logicValB))
    sim.step({
        'float_A': int(strValA, 2),
        'float_B': int(strValB, 2),
    })
    # print("\tvalu of 'expA' was: " + str(bin(sim.inspect(expA))))
    # print("\tvalu of 'expB' was: " + str(bin(sim.inspect(expB))))
    print("\tvalu of 'aGTbCompareDebug' was: " + str(bin(sim.inspect(abCompareDebug))))
    print("\tvalu of 'shiftRightAmountRev' was: " + str(bin(sim.inspect(shiftRightAmountRev))))


print('--- Simulation ---')
sim_trace.render_trace(symbol_len=5, segment_size=5)

c_value = sim.inspect(float_C)
print("The latest value of 'c' was: " + str(c_value))