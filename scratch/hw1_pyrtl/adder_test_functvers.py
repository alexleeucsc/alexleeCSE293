import pyrtl
from fplib import *
from math import pow
import random
pyrtl.reset_working_block()

#params
expLen = 8
manLen = 16

# state enums
WAITING, MULTIPLYING = [pyrtl.Const(x, bitwidth=2) for x in range(2)]


# ready_ab_reg = pyrtl.Register(1, 'ready_ab_reg')
# valid_c_reg = pyrtl.Register(1, 'valid_c_reg')
# mult_state = pyrtl.Register(1, 'mult_state')

#inputs
float_A = pyrtl.Input(expLen+manLen+1, 'float_A')
float_B = pyrtl.Input(expLen+manLen+1, 'float_B')
valid_ab = pyrtl.Input(1, 'valid_ab')
ready_c = pyrtl.Input(1, 'ready_c')
#outputs
float_C = pyrtl.Output(expLen+manLen+1, 'float_C')
valid_c = pyrtl.Output(1, 'valid_c')
ready_ab = pyrtl.Output(1, 'ready_ab')
#wires
signA = pyrtl.WireVector(1, 'signA')
expA = pyrtl.WireVector(expLen, 'expA')
manA = pyrtl.WireVector(manLen, 'manA')
signB = pyrtl.WireVector(1, 'signB')
expB = pyrtl.WireVector(expLen, 'expB')
manB = pyrtl.WireVector(manLen, 'manB')
signC = pyrtl.WireVector(1, 'signC')
expC = pyrtl.WireVector(expLen, 'expC')
manC = pyrtl.WireVector(manLen, 'manC')
#Wires
manBitsShiftFix = pyrtl.WireVector(manLen+1, 'manBitsShiftFix')
#debug wires
manCExtDebug = pyrtl.WireVector(manLen+1, 'manCExtDebug')
manCFixExtDebug = pyrtl.WireVector(manLen+1, 'manCFixExtDebug')

def addLogicFloat(float_A, float_B, float_C,
                        signA, expA, manA,
                        signB, expB, manB,
                        signC, expC, manC,
                        ready_ab, valid_ab, ready_c, valid_c,
                        manBitsShiftFix,
                        manCExtDebug,manCFixExtDebug):
    signA <<= float_A[0]
    expA <<= float_A[1:expLen+1]
    manA <<= float_A[expLen+1:]
    signB <<= float_B[0]
    expB <<= float_B[1:expLen+1]
    manB <<= float_B[expLen+1:]
    with pyrtl.conditional_assignment:
        #1: compare exp, keep bigger exp, then shiftright the mantissa of the smaller one
        with expA > expB:
            expC |= expA
            shiftRightAmount = expA - expB
            manBitsBAppend1 = pyrtl.concat(manB, pyrtl.Const("1'b1"))
            manBitsBFix = pyrtl.shift_right_arithmetic(manBitsBAppend1, shiftRightAmount) #should be same bit width as manLen+1
            manBitsShiftFix |= manBitsBFix
            manBitsAFix = pyrtl.concat(manA, pyrtl.Const("1'b1"))
        with expB <= expA:
            expC |= expA
            shiftRightAmount = expB - expA
            manBitsAAppend1 = pyrtl.concat(manA, pyrtl.Const("1'b1"))
            manBitsAFix = pyrtl.shift_right_arithmetic(manBitsAAppend1, shiftRightAmount) #should be same bit width as manLen+1
            manBitsShiftFix |= manBitsAFix
            manBitsBFix = pyrtl.concat(manB, pyrtl.Const("1'b1"))
        #2: add shifted mantissas. Consider sign bits
        with signA==pyrtl.Const("1'b1"):
            manBitsAFixSign = manBitsAFix * pyrtl.Const(-1,signed=True)
        with signA==pyrtl.Const("1'b0"):
            manBitsAFixSign = manBitsAFix
        with signB==pyrtl.Const("1'b1"):
            manBitsBFixSign = manBitsAFix * pyrtl.Const(-1,signed=True)
        with signB==pyrtl.Const("1'b0"):
            manBitsBFixSign = manBitsAFix
        manCExt = manBitsAFixSign + manBitsBFixSign
        manCExtDebug <<= manCExt
        #2b: if mantissa neg, turn pos and set sign bit
        with manCExt<0:
            signC |= pyrtl.Const("1'b1")
            manCFixExt = manCExt * pyrtl.Const(-1,signed=True)
        with manCExt>=0:
            signC |= pyrtl.Const("1'b1")
            manCFixExt = manCExt
        manCFixExtDebug <<= manCFixExt
        #3 correct mantissa len: first bit of mant is either 1 or 0:
        #if first bit is 1, mant overflow: fit starting from 1 into manC
        #to take care of overflow, add one to exp
        with manCFixExt[-1] == pyrtl.Const("1'b1"):
            manC |= manCFixExt #TEST: 053023 - does this auto-cuttoff from MSB?
            expCFix = expC+1
        with manCFixExt[-1] == pyrtl.Const("1'b0"):
            manC |= manCFixExt[:manLen]
            expCFix = expC
        #4 return fixed signals only:
        valid_c <<= pyrtl.Const("1'b1")
        ready_ab <<= pyrtl.Const("1'b1")
        float_C <<= pyrtl.concat_list([manC, expCFix, signC])



addLogicFloat(float_A, float_B, float_C,
                    signA, expA, manA,
                    signB, expB, manB,
                    signC, expC, manC,
                    ready_ab, valid_ab, ready_c, valid_c,
                    manBitsShiftFix,
                    manCExtDebug,manCFixExtDebug)

#sim_trace = pyrtl.SimulationTrace(register_value_map={digitMask: "6'b111111"})
sim_trace = pyrtl.SimulationTrace()
#bug 051523: https://pyrtl.readthedocs.io/en/latest/simtest.html
# register_value_map has format {reg:int}
sim = pyrtl.Simulation(tracer=sim_trace, register_value_map={   #digitMask: int(pow(2,6))-1,
                                                                #mult_state: 0,
                                                                #ready_ab_reg: 1,
                                                            })


for cycle in range(1):
    rand_flt_a = random.uniform(0.001,pow(2,5))
    rand_flt_b = random.uniform(0.001,pow(2,5))
    rand_flt_a = 27.975501666579657
    rand_flt_b = 5.791934863334932
    # rand_flt_a = 19.31798612365359
    # rand_flt_b = 22.768816354253484
    # rand_flt_a = 1.5649761142946192
    # rand_flt_b = 12.109807025821015
    # rand_flt_a = 20.46377914798672
    # rand_flt_b = 0.3842704582756764
    print("rand_flt_a",rand_flt_a)
    print("rand_flt_b",rand_flt_b)
    logicValA = float_to_Logicfloat(rand_flt_a,expLen,manLen)
    logicValB = float_to_Logicfloat(rand_flt_b,expLen,manLen)
    strValA = ''.join(reversed(logicValA))
    strValB = ''.join(reversed(logicValB))
    sim.step({
        'float_A': int(strValA, 2),
        'float_B': int(strValB, 2),
        'valid_ab':1,
        'ready_c':0,
    })
    float_C_val_int = sim.inspect(float_C)
    print("float_C_val_int",float_C_val_int)
    print("bin float_C_val_int",bin(float_C_val_int)[2:])
    float_C_val_str = zeroExtendLeft(bin(float_C_val_int)[2:], expLen+manLen+1)
    float_C_val = logicFloat_to_float([float_C_val_str[0], float_C_val_str[1:expLen+1], float_C_val_str[expLen+1:]], expLen, manLen)
    print("The latest value of 'float_C_val' was: " + str(float_C_val))
    print("\tvalue of 'signA' was: " + str(sim.inspect(signA)))
    print("\tvalu of 'expA' was: " + str(bin(sim.inspect(expA))))
    print("\tvalu of 'manA' was: " + str(bin(sim.inspect(manA))))

    print("\tvalue of 'signB' was: " + str(sim.inspect(signB)))
    print("\tvalu of 'expB' was: " + str(bin(sim.inspect(expB))))
    print("\tvalu of 'manB' was: " + str(bin(sim.inspect(manB))))
    
    print("\tvalue of 'signC' was: " + str(sim.inspect(signC)))
    print("\tvalu of 'expC' was: " + str(bin(sim.inspect(expC))))
    print("\tvalu of 'manC' was: " + str(bin(sim.inspect(manC))))
    print("-----DEBUG VALUES-----")
    print("\tvalu of 'manCExtDebug' was: " + str(bin(sim.inspect(manCExtDebug))))
    print("\tvalu of 'manCFixExtDebug' was: " + str(bin(sim.inspect(manCFixExtDebug))))

    print("\traw flaot C out: float_C_val_int", bin(float_C_val_int))
    pyOut = rand_flt_a + rand_flt_b
    print("logfloat rep C:",[float_C_val_str[0], float_C_val_str[1:expLen+1], float_C_val_str[expLen+1:]])
    assert(abs(float_C_val-pyOut)<1)


print('--- Simulation ---')
sim_trace.render_trace(symbol_len=5, segment_size=5)

c_value = sim.inspect(float_C)
print("The latest value of 'c' was: " + str(c_value))