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
signA = pyrtl.WireVector(1, 'signA')
expA = pyrtl.WireVector(expLen, 'expA')
manA = pyrtl.WireVector(manLen, 'manA')
signB = pyrtl.WireVector(1, 'signB')
expB = pyrtl.WireVector(expLen, 'expB')
manB = pyrtl.WireVector(manLen, 'manB')
#regularized wires
float_A_pos = pyrtl.WireVector(expLen+manLen+1, 'float_A_pos')
float_B_pos = pyrtl.WireVector(expLen+manLen+1, 'float_B_pos')
float_A_reg = pyrtl.WireVector(expLen+manLen+1, 'float_A_reg')
float_B_reg = pyrtl.WireVector(expLen+manLen+1, 'float_B_reg')
float_C_p1 = pyrtl.WireVector(expLen+manLen+1, 'float_C_p1')
float_A_reg_registers = pyrtl.Register(expLen+manLen+1, 'float_A_reg_registers')
float_B_reg_registers = pyrtl.Register(expLen+manLen+1, 'float_B_reg_registers')
#wires def in algo
shiftRightB = pyrtl.WireVector(expLen+1, 'shiftRightB')
recGuessP = pyrtl.WireVector(manLen+expLen+1, 'recGuessP')
recGuessP2 = pyrtl.WireVector(manLen+expLen+1, 'recGuessP2')
#recGuess = pyrtl.WireVector(manLen+expLen+1, 'recGuess')
iterVal1 = pyrtl.WireVector(manLen+expLen+1, 'iterVal1')
iterVal1P = pyrtl.WireVector(manLen+expLen+1, 'iterVal1P')
iterVal2 = pyrtl.WireVector(manLen+expLen+1, 'iterVal2')
iterVal3 = pyrtl.WireVector(manLen+expLen+1, 'iterVal3')
iterVal4 = pyrtl.WireVector(manLen+expLen+1, 'iterVal4')
#
signC = pyrtl.WireVector(1, 'signC')
#debug wires
#ready_cisokay = pyrtl.WireVector(1, 'ready_cisokay')

#regs to keep iterVal1
recGuessWire = pyrtl.WireVector(manLen+expLen+1, 'recGuessWire')
recGuess = pyrtl.Register(manLen+expLen+1, 'recGuess')
iterCount = pyrtl.Register(manLen+expLen+1, 'iterCount')

with pyrtl.conditional_assignment as condAssignObj:
    #if waiting, do all setup
    signA <<= float_A[expLen+manLen]
    expA <<= float_A[manLen:expLen+manLen]
    manA <<= float_A[:manLen]
    signB <<= float_B[expLen+manLen]
    expB <<= float_B[manLen:expLen+manLen]
    manB <<= float_B[:manLen]
    float_A_pos <<= pyrtl.concat_list([manA, expA, pyrtl.Const("1'b0")])
    float_B_pos <<= pyrtl.concat_list([manB, expB, pyrtl.Const("1'b0")])
    with state == WAITING:
        valid_c |= pyrtl.Const(0)
        ready_ab |= pyrtl.Const(1)
        with valid_ab:
            #1: normalize inputs with shifting: subtract each exp by divisor exp + 1
            # expASub |= expA + ~expB + 1 - pyrtl.Const(str(expLen+1)+"'b1"+("0"*(expLen)))
            # expBSub |= expB + ~expB + 1 - pyrtl.Const(str(expLen+1)+"'b1"+("0"*(expLen)))
            shiftRightB |= expB + 1 - pyrtl.Const(str(expLen)+"'b1"+("0"*(expLen-1)))
            shiftLogicFloatObj1 = shiftTestClass("shiftobj1",expLen,manLen)
            shiftLogicFloatObj1.shiftRightLogicFloat(float_A_pos, float_A_reg, shiftRightB)
            shiftLogicFloatObj2 = shiftTestClass("shiftobj2",expLen,manLen)
            shiftLogicFloatObj2.shiftRightLogicFloat(float_B_pos, float_B_reg, shiftRightB)
            #2: hard assign initial guess
            c1Logic = float_to_Logicfloat(48/17, expLen, manLen)
            c2Logic = float_to_Logicfloat(32/17, expLen, manLen)
            c1Wire = pyrtl.Const(str(1+manLen+expLen)+"'b"+"".join(c1Logic))
            c2Wire = pyrtl.Const(str(1+manLen+expLen)+"'b"+"".join(c2Logic))
            #2b: addlogic doesn't return anything: it just connects wires you give it
            multiplyLogicFloatObj1 = multTestClass("multobj1",expLen,manLen)
            multiplyLogicFloatObj1.multiplyLogicFloat(c2Wire, float_B_reg, recGuessP)
            recGuessP2 |= pyrtl.concat(~recGuessP[manLen+expLen], recGuessP[:manLen+expLen])
            addTestObj1 = addTestClass("addobj1",expLen,manLen)
            addTestObj1.addLogicFloat(c1Wire, recGuessP2, recGuessWire)
            recGuess.next |= recGuessWire
            float_A_reg_registers.next |= float_A_reg
            float_B_reg_registers.next |= float_B_reg
            #3: when the input is ready, recGuess was given the rign value
            state.next |= MULTIPLYING
        with ~valid_ab:
            state.next |= WAITING
    #if multiplying, do calc and check
    with state == MULTIPLYING:
        #valid_c |= pyrtl.Const(0)
        ready_ab |= pyrtl.Const(0)
        #1: calc each step
        multiplyLogicFloatObj2 = multTestClass("multobj2",expLen,manLen)
        multiplyLogicFloatObj2.multiplyLogicFloat(float_B_reg_registers, recGuess, iterVal1)   #(div*rec_guess)
        iterVal1P <<= pyrtl.concat(~iterVal1[manLen+expLen], iterVal1[:manLen+expLen])                                   #-(div*rec_guess)
        c3Logic = float_to_Logicfloat(1, expLen, manLen)                                        #get 1
        addTestObj2 = addTestClass("addobj2",expLen,manLen)
        addTestObj2.addLogicFloat(pyrtl.Const(str(1+manLen+expLen)+"'b"+"".join(c3Logic)), iterVal1P, iterVal2)   #(1-(div*rec_guess))
        multiplyLogicFloatObj3 = multTestClass("multobj3",expLen,manLen)
        multiplyLogicFloatObj3.multiplyLogicFloat(recGuess, iterVal2, iterVal3)  #recGuess*(1-(div*rec_guess))
        addTestObj3 = addTestClass("addobj3",expLen,manLen)
        addTestObj3.addLogicFloat(recGuess, iterVal3, iterVal4)       #recGuess + recGuess*(1-(div*rec_guess))
        #2: if regs stop changing, OR max_iter steps have passed, set output to valid and set state to DONE
        #recGuess.next |= iterVal4
        # signC <<= signA ^ signB
        recGuess.next |= pyrtl.concat_list([iterVal4[:manLen],
                                            iterVal4[manLen:expLen+manLen],
                                            iterVal4[expLen+manLen]])
        multiplyLogicFloatObj4 = multTestClass("multobj4",expLen,manLen)
        # multiplyLogicFloatObj4.multiplyLogicFloat(float_A_reg_registers, iterVal4, float_C)  #recGuess*(1-(div*rec_guess))
        with (iterVal4 == recGuess) | (iterCount == pyrtl.Const(max_iter)) :
            state.next |= DONE
            iterCount.next |= 0
            valid_c |= pyrtl.Const(0)
        with otherwise:
            state.next |= MULTIPLYING
            iterCount.next |= iterCount + 1
            valid_c |= pyrtl.Const(0)
    with state == DONE:
        multiplyLogicFloatObj4.multiplyLogicFloat(float_A_reg_registers, iterVal4, float_C_p1)
        signC |= signA ^ signB
        float_C |= pyrtl.concat_list([float_C_p1[:manLen],
                                            float_C_p1[manLen:expLen+manLen],
                                            signC])
        valid_c |= pyrtl.Const(1)
        ready_ab |= pyrtl.Const(0)
        #if output is signaled as 'ready', assume output has been read and exitready_c
        with ready_c:
            state.next |= WAITING
            float_A_reg_registers.next  |= 0
            float_B_reg_registers.next  |= 0
            recGuess.next               |= 0
            iterCount.next              |= 0
        with otherwise:
            state.next |= DONE

#sim_trace = pyrtl.SimulationTrace(register_value_map={digitMask: "6'b111111"})
sim_trace = pyrtl.SimulationTrace()
#bug 051523: https://pyrtl.readthedocs.io/en/latest/simtest.html
# register_value_map has format {reg:int}
sim = pyrtl.Simulation(tracer=sim_trace, register_value_map={   #digitMask: int(pow(2,6))-1,
                                                                #mult_state: 0,
                                                                #ready_ab_reg: 1,
                                                            })

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
    while(sim.inspect(valid_c) == 0):
        sim.step({
            'float_A': int(strValA, 2),
            'float_B': int(strValB, 2),
            'valid_ab':1,
            'ready_c':0,
        })
        recGuess_int = sim.inspect(recGuess)
        recGuess_str = zeroExtendLeft(bin(recGuess_int)[2:], expLen+manLen+1)
        recGuess_val = logicFloat_to_float([recGuess_str[0], recGuess_str[1:expLen+1], recGuess_str[expLen+1:]], expLen, manLen)
    float_C_outputfloat = binWireToFloat(float_C, expLen+manLen+1)
    pyOut = rand_flt_a / rand_flt_b
    print(float_C_outputfloat, "vs", pyOut)
    assert(abs(float_C_outputfloat-pyOut)<1)
    for _ in range(2):
        sim.step({
            'float_A': int(strValA, 2),
            'float_B': int(strValB, 2),
            'valid_ab':0,
            'ready_c':1,
        })
    print("\n")

