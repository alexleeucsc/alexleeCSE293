import pyrtl
from fplib import *
from math import pow
pyrtl.reset_working_block()

#params
expLen = 4
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
#debugWires
manCLongWire = pyrtl.WireVector(2+manLen*3, 'manCLongWire')

def multiplyLogicFloat(float_A, float_B, float_C,
                        signA, expA, manA,
                        signB, expB, manB,
                        ready_ab, valid_ab, ready_c, valid_c,
                        manCLongWire):
    signA <<= float_A[0]
    expA <<= float_A[1:expLen+1]
    manA <<= float_A[expLen+1:]
    signB <<= float_B[0]
    expB <<= float_B[1:expLen+1]
    manB <<= float_B[expLen+1:]
    with pyrtl.conditional_assignment:
        print("binary string:",str(expLen)+"'b1"+('0'*(expLen-1)))
        expC = expA+expB-pyrtl.Const(str(expLen)+"'b1"+('0'*(expLen-1)))
        #multiply manC, shift right until first bit is a 1
        manCLong = pyrtl.concat(pyrtl.Const("1'b1"), manA) * pyrtl.concat(pyrtl.Const("1'b1"), manB)
        manCLongWire <<= manCLong[len(manCLong)-manLen-2:-2]
        with manCLong[0] == pyrtl.Const("1'b1"):
            float_C |= pyrtl.concat_list([manCLongWire, (expA+expB-pyrtl.Const(str(expLen)+"'b1"+('0'*(expLen-1))))[expLen], signA^signB])
        with manCLong[0] == pyrtl.Const("1'b0"):
            float_C |= pyrtl.concat_list([manCLongWire, (expA+expB-pyrtl.Const(str(expLen)+"'b1"+('0'*(expLen-1))))[expLen], signA^signB])
            #float_C |= pyrtl.concat_list([manCLong[1:1+expLen], (expA+expB-pyrtl.Const(str(expLen)+"'b1"+('0'*(expLen-1))))[expLen], signA^signB])
    valid_c <<= pyrtl.Const("1'b1")
    ready_ab <<= pyrtl.Const("1'b1")
    # valid_c_reg <<= pyrtl.Const("1'b1")
    # mult_state <<= pyrtl.Const("1'b1")

multiplyLogicFloat(float_A, float_B, float_C,
                    signA, expA, manA,
                    signB, expB, manB,
                    ready_ab, valid_ab, ready_c, valid_c,
                    manCLongWire)

#sim_trace = pyrtl.SimulationTrace(register_value_map={digitMask: "6'b111111"})
sim_trace = pyrtl.SimulationTrace()
#bug 051523: https://pyrtl.readthedocs.io/en/latest/simtest.html
# register_value_map has format {reg:int}
sim = pyrtl.Simulation(tracer=sim_trace, register_value_map={   #digitMask: int(pow(2,6))-1,
                                                                #mult_state: 0,
                                                                #ready_ab_reg: 1,
                                                            })


for cycle in range(2):
    logicValA = float_to_Logicfloat(34.21,expLen,manLen)
    logicValB = float_to_Logicfloat(17.23,expLen,manLen)
    strValA = ''.join(reversed(logicValA))
    strValB = ''.join(reversed(logicValB))
    sim.step({
        'float_A': int(strValA, 2),
        'float_B': int(strValB, 2),
        'valid_ab':1,
        'ready_c':0,
    })
    float_C_val_int = sim.inspect(float_C)
    print(float_C_val_int)
    print(bin(float_C_val_int)[2:])
    float_C_val_str = zeroExtendLeft(bin(float_C_val_int)[2:], expLen+manLen+1)
    float_C_val = logicFloat_to_float([float_C_val_str[0], float_C_val_str[1:expLen+1], float_C_val_str[expLen+1:]], expLen, manLen)
    print("The latest value of 'float_C_val' was: " + str(float_C_val))
    print("\tvalue of 'signA' was: " + str(sim.inspect(signA)))
    print("\tvalu of 'expA' was: " + str(bin(sim.inspect(expA))))
    print("\tvalu of 'manA' was: " + str(bin(sim.inspect(manA))))

    print("\tvalue of 'signB' was: " + str(sim.inspect(signB)))
    print("\tvalu of 'expB' was: " + str(bin(sim.inspect(expB))))
    print("\tvalu of 'manB' was: " + str(bin(sim.inspect(manB))))
    
    #print("\tvalue of 'signC' was: " + str(sim.inspect(signC)))
    #print("\tvalu of 'expC' was: " + str(bin(sim.inspect(expC))))
    #print("\tvalu of 'manC' was: " + str(bin(sim.inspect(manC))))
    print("\tvalu of 'manCLongWire' was: " + str(bin(sim.inspect(manCLongWire))))

    print("\traw flaot C out: float_C_val_int", bin(float_C_val_int))
    print("logfloat rep C:",[float_C_val_str[0], float_C_val_str[1:expLen+1], float_C_val_str[expLen+1:]])


print('--- Simulation ---')
sim_trace.render_trace(symbol_len=5, segment_size=5)

c_value = sim.inspect(float_C)
print("The latest value of 'c' was: " + str(c_value))