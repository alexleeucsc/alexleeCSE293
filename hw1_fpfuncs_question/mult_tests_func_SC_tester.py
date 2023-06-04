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
#outputs
float_C = pyrtl.Output(expLen+manLen+1, 'float_C')

def multiplyLogicFloat(float_A, float_B, float_C,condAssignObj):
    #wires
    signA = pyrtl.WireVector(1, 'signA')
    expA = pyrtl.WireVector(expLen, 'expA')
    manA = pyrtl.WireVector(manLen, 'manA')
    signB = pyrtl.WireVector(1, 'signB')
    expB = pyrtl.WireVector(expLen, 'expB')
    manB = pyrtl.WireVector(manLen, 'manB')
    #debugWires
    manCLongWire = pyrtl.WireVector(2+manLen*2, 'manCLongWire')
    manCLongWireCut = pyrtl.WireVector(1+manLen, 'manCLongWireCut')
    expCDebug = pyrtl.WireVector(expLen+1, 'expCDebug')
    manCLongDeciderDebug = pyrtl.WireVector(1, 'manCLongDeciderDebug')
    signA <<= float_A[0]
    expA <<= float_A[1:expLen+1]
    manA <<= float_A[expLen+1:]
    signB <<= float_B[0]
    expB <<= float_B[1:expLen+1]
    manB <<= float_B[expLen+1:]
    with pyrtl.conditional_assignment:
        print("binary string:",str(expLen)+"'b1"+('0'*(expLen-1)))
        expC = expA+expB-pyrtl.Const(str(expLen)+"'b1"+('0'*(expLen-1)))
        expCDebug <<= expC
        #multiply manC, shift right until first bit is a 1
        manCLong = pyrtl.concat(pyrtl.Const("1'b1"), manA) * pyrtl.concat(pyrtl.Const("1'b1"), manB)
        print("@@@@@",len(manCLong),"@@@@@")
        manCLongWireCut <<= pyrtl.concat(pyrtl.Const("1'b1"), manA) * pyrtl.concat(pyrtl.Const("1'b1"), manB)
        manCLongWire <<= manCLong[len(manCLong)-manLen-2:-2]
        manCLongDeciderDebug <<= manCLong[-1]
        with manCLong[-1] == pyrtl.Const("1'b1"):
            #BUG 052923 - manCLong bit index wrong, should be -1
            #BUG 052923 - the -1 and -2 were mixed
            #BUG 052923 - add one to exp when first bit is a 1 and you are cutting off less
            float_C |= pyrtl.concat_list([manCLong[len(manCLong)-manLen-1:-1], (expA+expB-pyrtl.Const(str(expLen)+"'b1"+('0'*(expLen-1))))+1, pyrtl.Const("1'b0")])
        with manCLong[-1] == pyrtl.Const("1'b0"):
            float_C |= pyrtl.concat_list([manCLong[len(manCLong)-manLen-2:-2], (expA+expB-pyrtl.Const(str(expLen)+"'b1"+('0'*(expLen-1)))), pyrtl.Const("1'b0")])
            #float_C |= pyrtl.concat_list([manCLong[1:1+expLen], (expA+expB-pyrtl.Const(str(expLen)+"'b1"+('0'*(expLen-1))))[expLen], signA^signB])
    # valid_c_reg <<= pyrtl.Const("1'b1")
    # mult_state <<= pyrtl.Const("1'b1")


if __name__ == "__main__":
    for cycle in range(10000):
        rand_flt_a = random.uniform(0.001,pow(2,5))
        rand_flt_b = random.uniform(0.001,pow(2,5))
        # rand_flt_a = 27.975501666579657
        # rand_flt_b = 5.791934863334932
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
        })
        float_C_val_int = sim.inspect(float_C)
        print("float_C_val_int",float_C_val_int)
        print("bin float_C_val_int",bin(float_C_val_int)[2:])
        float_C_val_str = zeroExtendLeft(bin(float_C_val_int)[2:], expLen+manLen+1)
        float_C_val = logicFloat_to_float([float_C_val_str[0], float_C_val_str[1:expLen+1], float_C_val_str[expLen+1:]], expLen, manLen)
        # print("The latest value of 'float_C_val' was: " + str(float_C_val))
        # print("\tvalue of 'signA' was: " + str(sim.inspect(signA)))
        # print("\tvalu of 'expA' was: " + str(bin(sim.inspect(expA))))
        # print("\tvalu of 'manA' was: " + str(bin(sim.inspect(manA))))

        # print("\tvalue of 'signB' was: " + str(sim.inspect(signB)))
        # print("\tvalu of 'expB' was: " + str(bin(sim.inspect(expB))))
        # print("\tvalu of 'manB' was: " + str(bin(sim.inspect(manB))))
        
        # #print("\tvalue of 'signC' was: " + str(sim.inspect(signC)))
        # #print("\tvalu of 'expC' was: " + str(bin(sim.inspect(expC))))
        # #print("\tvalu of 'manC' was: " + str(bin(sim.inspect(manC))))
        # print("\tvalu of 'manCLongWire' was: " + str(bin(sim.inspect(manCLongWire))))
        # print("\tvalu of 'expCDebug' was: " + str(bin(sim.inspect(expCDebug))))
        # print("\tvalu of 'manCLongDeciderDebug' was: " + str(bin(sim.inspect(manCLongDeciderDebug))))
        # print("\tvalu of 'manCLongWireCut' was: " + str(bin(sim.inspect(manCLongWireCut))))

        print("\traw flaot C out: float_C_val_int", bin(float_C_val_int))
        pyOut = rand_flt_a * rand_flt_b
        print("logfloat rep C:",[float_C_val_str[0], float_C_val_str[1:expLen+1], float_C_val_str[expLen+1:]])
        assert(abs(float_C_val-pyOut)<1)


    print('--- Simulation ---')
    sim_trace.render_trace(symbol_len=5, segment_size=5)

    c_value = sim.inspect(float_C)
    print("The latest value of 'c' was: " + str(c_value))