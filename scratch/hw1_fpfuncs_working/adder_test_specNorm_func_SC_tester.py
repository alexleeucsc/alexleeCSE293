from pyrtl import *
from fplib import *
from math import pow
import random
from providedLib import prioritized_mux

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
#outputs
float_C = pyrtl.Output(expLen+manLen+1, 'float_C')

def addLogicFloat(float_A, float_B, float_C):
    #wires
    signA = pyrtl.WireVector(1, 'signA')
    expA = pyrtl.WireVector(expLen, 'expA')
    manA = pyrtl.WireVector(manLen, 'manA')
    signB = pyrtl.WireVector(1, 'signB')
    expB = pyrtl.WireVector(expLen, 'expB')
    manB = pyrtl.WireVector(manLen, 'manB')
    signC = pyrtl.WireVector(1, 'signC')
    expC = pyrtl.WireVector(expLen, 'expC')
    manC = pyrtl.WireVector(manLen, 'manCFinal')

    #Wires
    #manBitsShiftFix = pyrtl.WireVector(manLen+1, 'manBitsShiftFix')
    #manBitsAFixSign/manBitsBFixSign have 2 additional bits:
    #one for the added '1', one to functionally store the sign bit
    #the extra sign bit needs to be added early otherwise it isn't flipped
    manBitsAFix = pyrtl.WireVector(manLen+1, 'manBitsAFix')
    manBitsBFix = pyrtl.WireVector(manLen+1, 'manBitsBFix')
    shiftRightAmount = pyrtl.WireVector(expLen+1, 'shiftRightAmount')
    #manBitsAFixSign/manBitsBFixSign have 2 additional bits:
    #one for the added '1', one to functionally store the sign bit
    manBitsAFixSign = pyrtl.WireVector(manLen+3, 'manBitsAFixSign')
    manBitsBFixSign = pyrtl.WireVector(manLen+3, 'manBitsBFixSign')
    manCExt = pyrtl.WireVector(manLen+3, 'manCExt')
    manCFixExt = pyrtl.WireVector(manLen+2, 'manCFixExt')
    #intermediate exp wires
    expCMid = pyrtl.WireVector(expLen, 'expCMid')
    #first1tree wires
    fisrtOneIdxManC = pyrtl.WireVector(256, 'fisrtOneIdx')
    #fisrtOneIdxManCSHAM = pyrtl.WireVector(256, 'fisrtOneIdxManCSHAM')

    #debug wires
    manCExtDebug = pyrtl.WireVector(manLen+2, 'manCExtDebug')
    manCFixExtDebug = pyrtl.WireVector(manLen+1, 'manCFixExtDebug')
    #abCompareDebug = pyrtl.WireVector(1, 'abCompareDebug')

    signA <<= float_A[0]
    expA <<= float_A[1:expLen+1]
    manA <<= float_A[expLen+1:]
    signB <<= float_B[0]
    expB <<= float_B[1:expLen+1]
    manB <<= float_B[expLen+1:]

    expCMid <<= select((expA >= expB), expA, expB)
    shiftRightAmount <<= select((expA >= expB), expA + ~expB + 1 - pyrtl.Const(str(expLen+1)+"'b1"+("0"*(expLen))), expB + ~expA + 1 - pyrtl.Const(str(expLen+1)+"'b1"+("0"*(expLen))))
    manBitsBFix <<= select((expA >= expB), pyrtl.shift_right_logical(pyrtl.concat(pyrtl.Const("1'b1"), manB), shiftRightAmount), pyrtl.concat(pyrtl.Const("1'b1"), manB))
    manBitsAFix <<= select((expA >= expB), pyrtl.concat(pyrtl.Const("1'b1"), manA), pyrtl.shift_right_logical(pyrtl.concat(pyrtl.Const("1'b1"), manA), shiftRightAmount))

    manBitsAFixSign <<= select(signA==pyrtl.Const("1'b1"), pyrtl.concat(pyrtl.Const("2'b11"), (~manBitsAFix + 1)[:manLen+1]), manBitsAFix)

    manBitsBFixSign <<= select(signB==pyrtl.Const("1'b1"), pyrtl.concat(pyrtl.Const("2'b11"), (~manBitsBFix + 1)[:manLen+1]), manBitsBFix)
    manCExt <<= manBitsAFixSign + manBitsBFixSign
    manCExtDebug <<= manCExt

    signC <<= select(manCExt[-1] == pyrtl.Const("1'b1"), pyrtl.Const("1'b1"), pyrtl.Const("1'b0"))
    manCFixExt <<= select(manCExt[-1] == pyrtl.Const("1'b1"), ~manCExt[:manLen+2] + 1, manCExt[:manLen+2])
    manCFixExtDebug <<= manCFixExt

    vals = [Const(i) for i in range(manLen+2)]
    fisrtOneIdxManC <<= select(manCFixExt[-1] == pyrtl.Const("1'b1"), pyrtl.Const(1), prioritized_mux(manCFixExt, vals))
    expC <<= select(manCFixExt[-1] == pyrtl.Const("1'b1"), expCMid+1, expCMid - (manLen-fisrtOneIdxManC))
    manC <<= select(manCFixExt[-1] == pyrtl.Const("1'b1"), manCFixExt[1:manLen+1], pyrtl.shift_left_logical(manCFixExt, manLen-fisrtOneIdxManC))


    #4 return fixed signals only:
    float_C <<= pyrtl.concat_list([manC, expC, signC])



# addLogicFloat(float_A, float_B, float_C,
#                     signA, expA, manA,
#                     signB, expB, manB,
#                     signC, expC, manC,
#                     ready_ab, valid_ab, ready_c, valid_c)

addLogicFloat(float_A, float_B, float_C)

#sim_trace = pyrtl.SimulationTrace(register_value_map={digitMask: "6'b111111"})
sim_trace = pyrtl.SimulationTrace()
#bug 051523: https://pyrtl.readthedocs.io/en/latest/simtest.html
# register_value_map has format {reg:int}
sim = pyrtl.Simulation(tracer=sim_trace, register_value_map={   #digitMask: int(pow(2,6))-1,
                                                                #mult_state: 0,
                                                                #ready_ab_reg: 1,
                                                            })

if __name__ == "__main__":
    for cycle in range(1000):
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
        print("logicValA",logicValA)
        print("logicValB",logicValB)
        strValA = ''.join(reversed(logicValA))
        strValB = ''.join(reversed(logicValB))
        sim.step({
            'float_A': int(strValA, 2),
            'float_B': int(strValB, 2),
        })
        float_C_val_int = sim.inspect(float_C)
        print("float_C_val_int",float_C_val_int)
        print("bin float_C_val_int",bin(float_C_val_int)[2:])
        float_C_val_str = zeroExtendLeft(bin(float_C_val_int)[2:], expLen+manLen+1)
        float_C_val = logicFloat_to_float([float_C_val_str[0], float_C_val_str[1:expLen+1], float_C_val_str[expLen+1:]], expLen, manLen)
        print("The latest value of 'float_C_val' was: " + str(float_C_val))
        # print("\tvalue of 'signA' was: " + str(sim.inspect(signA)))
        # print("\tvalu of 'expA' was: " + str(bin(sim.inspect(expA))))
        # print("\tvalu of 'manA' was: " + str(bin(sim.inspect(manA))))

        # print("\tvalue of 'signB' was: " + str(sim.inspect(signB)))
        # print("\tvalu of 'expB' was: " + str(bin(sim.inspect(expB))))
        # print("\tvalu of 'manB' was: " + str(bin(sim.inspect(manB))))
        
        # print("\tvalue of 'signC' was: " + str(sim.inspect(signC)))
        # print("\tvalu of 'expC' was: " + str(bin(sim.inspect(expC))))
        # print("\tvalu of 'manC' was: " + str(bin(sim.inspect(manC))))
        # print("-----DEBUG VALUES-----")
        # print("\tvalu of 'manCExtDebug' was: " + str(bin(sim.inspect(manCExtDebug))))
        # print("\tvalu of 'manCFixExtDebug' was: " + str(bin(sim.inspect(manCFixExtDebug))))
        # print("\tvalu of 'manBitsAFix' was: " + str(bin(sim.inspect(manBitsAFix))))
        # print("\tvalu of 'manBitsBFix' was: " + str(bin(sim.inspect(manBitsBFix))))
        # print("\tvalu of 'manBitsAFixSign' was: " + str(bin(sim.inspect(manBitsAFixSign))))
        # print("\tvalu of 'manBitsBFixSign' was: " + str(bin(sim.inspect(manBitsBFixSign))))
        # print("\tvalu of 'shiftRightAmount' was: " + str(bin(sim.inspect(shiftRightAmount))))
        # print("-----TMP VALUES-----")
        # print("\tvalu of 'fisrtOneIdxManC' was: " + str(bin(sim.inspect(fisrtOneIdxManC)))) 
        # print("\tvalu of 'fisrtOneIdxManCSHAM' was: " + str(bin(sim.inspect(fisrtOneIdxManCSHAM))))

        print("\traw flaot C out: float_C_val_int", bin(float_C_val_int))
        pyOut = rand_flt_a + rand_flt_b
        print("logfloat rep C:",[float_C_val_str[0], float_C_val_str[1:expLen+1], float_C_val_str[expLen+1:]])
        assert(abs(float_C_val-pyOut)<1)


    print('--- Simulation ---')
    sim_trace.render_trace(symbol_len=5, segment_size=5)

    c_value = sim.inspect(float_C)
    print("The latest value of 'c' was: " + str(c_value))