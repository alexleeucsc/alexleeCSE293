from pyrtl import *
from fplib import *
from math import pow
import random
from providedLib import prioritized_mux
from adder_test_specNorm_obj_SC_tester import *
from mult_tests_obj_SC_tester import *
from shifter_tests_obj_SC_tester import *

pyrtl.reset_working_block()

#params
expLen = 8
manLen = 16
max_iter = 30

# state enums
WAITING, MULTIPLYING, DONE = [pyrtl.Const(x, bitwidth=2) for x in range(3)]

#inputs
float_A = pyrtl.Input(expLen+manLen+1, 'float_A')
float_B = pyrtl.Input(expLen+manLen+1, 'float_B')
valid_ab = pyrtl.Input(1, 'valid_ab')
ready_c = pyrtl.Input(1, 'ready_c')
#outputs
# float_C = pyrtl.Output(expLen+manLen+1, 'float_C')
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
# signC = pyrtl.WireVector(1, 'signC')
# expC = pyrtl.WireVector(expLen, 'expC')
# manC = pyrtl.WireVector(manLen, 'manCFinal')
#inner wires
# manBitsAFix = pyrtl.WireVector(manLen+1, 'manBitsAFix')
# manBitsBFix = pyrtl.WireVector(manLen+1, 'manBitsBFix')
# shiftRightAmount = pyrtl.WireVector(expLen+1, 'shiftRightAmount')

#wires def in algo
expASub = pyrtl.WireVector(expLen+1, 'expASub')
expBSub = pyrtl.WireVector(expLen+1, 'expBSub')
recGuessP = pyrtl.WireVector(manLen+expLen+1, 'recGuessP')
recGuessP2 = pyrtl.WireVector(manLen+expLen+1, 'recGuessP2')
#recGuess = pyrtl.WireVector(manLen+expLen+1, 'recGuess')
iterVal1 = pyrtl.WireVector(manLen+expLen+1, 'iterVal1')
iterVal1P = pyrtl.WireVector(manLen+expLen+1, 'iterVal1P')
iterVal2 = pyrtl.WireVector(manLen+expLen+1, 'iterVal2')
iterVal3 = pyrtl.WireVector(manLen+expLen+1, 'iterVal3')
iterVal4 = pyrtl.WireVector(manLen+expLen+1, 'iterVal4')

#regs to keep iterVal1
recGuessWire = pyrtl.WireVector(manLen+expLen+1, 'recGuessWire')
recGuess = pyrtl.Register(manLen+expLen+1, 'recGuess')
iterCount = pyrtl.Register(manLen+expLen+1, 'iterCount')

with pyrtl.conditional_assignment as condAssignObj:
    #if waiting, do all setup
    signA <<= float_A[0]
    expA <<= float_A[1:expLen+1]
    manA <<= float_A[expLen+1:]
    signB <<= float_B[0]
    expB <<= float_B[1:expLen+1]
    manB <<= float_B[expLen+1:]
    with state == WAITING:
        valid_c |= pyrtl.Const(0)
        ready_ab |= pyrtl.Const(1)
        #1: normalize inputs with shifting: subtract each exp by divisor exp + 1
        expASub |= expA + ~expB + 1 - pyrtl.Const(str(expLen+1)+"'b1"+("0"*(expLen)))
        expBSub |= expB + ~expB + 1 - pyrtl.Const(str(expLen+1)+"'b1"+("0"*(expLen)))

        #2: hard assign initial guess
        c1Logic = float_to_Logicfloat(48/17, expLen, manLen)
        c2Logic = float_to_Logicfloat(32/17, expLen, manLen)
        #2b: addlogic doesn't return anything: it just connects wires you give it
        multiplyLogicFloatObj1 = multTestClass("multobj1",expLen,manLen)
        multiplyLogicFloatObj1.multiplyLogicFloat(pyrtl.Const(str(1+manLen+expLen)+"'b"+"".join(c2Logic)), float_B, recGuessP)
        recGuessP2 |= pyrtl.concat(recGuessP[0], recGuessP[1:])
        addTestObj1 = addTestClass("addobj1",expLen,manLen)
        addTestObj1.addLogicFloat(pyrtl.Const(str(1+manLen+expLen)+"'b"+"".join(c1Logic)), recGuessP2, recGuessWire)
        recGuess.next |= recGuessWire
        #3: when the input is ready, recGuess was given the rign value
        with valid_ab:
            state.next |= MULTIPLYING
    #if multiplying, do calc and check
    with state == MULTIPLYING:
        valid_c |= pyrtl.Const(0)
        ready_ab |= pyrtl.Const(0)
        #1: calc each step
        multiplyLogicFloatObj2 = multTestClass("multobj2",expLen,manLen)
        multiplyLogicFloatObj2.multiplyLogicFloat(float_B, recGuess, iterVal1)   #(div*rec_guess)
        iterVal1P <<= pyrtl.concat(iterVal1[0], iterVal1[1:])                                   #-(div*rec_guess)
        c3Logic = float_to_Logicfloat(1, expLen, manLen)                                        #get 1
        addTestObj2 = addTestClass("addobj2",expLen,manLen)
        addTestObj2.addLogicFloat(pyrtl.Const(str(1+manLen+expLen)+"'b"+"".join(c3Logic)), iterVal1P, iterVal2)   #(1-(div*rec_guess))
        multiplyLogicFloatObj3 = multTestClass("multobj3",expLen,manLen)
        multiplyLogicFloatObj3.multiplyLogicFloat(recGuess, iterVal2, iterVal3)  #recGuess*(1-(div*rec_guess))
        addTestObj3 = addTestClass("addobj3",expLen,manLen)
        addTestObj3.addLogicFloat(recGuess, iterVal3, iterVal4)       #recGuess + recGuess*(1-(div*rec_guess))
        #2: if regs stop changing, OR max_iter steps have passed, set output to valid and set state to DONE
        recGuess.next |= recGuessWire
        with (iterVal4 == recGuess) | (iterCount == pyrtl.Const(max_iter)) :
            state.next |= DONE
            iterCount.next |= 0
        with otherwise:
            iterCount.next |= iterCount + 1
    with state == DONE:
        valid_c |= pyrtl.Const(1)
        ready_ab |= pyrtl.Const(0)
        #if output is signaled as 'ready', assume output has been read and exit
        with ready_c:
            state.next |= WAITING

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
    a_sign = 121
    b_sign = 11
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
    for cycle in range(5):
        sim.step({
            'float_A': int(strValA, 2),
            'float_B': int(strValB, 2),
            'valid_ab':1,
            'ready_c':0,
        })
        recGuess_int = sim.inspect(recGuess)
        print("recGuess_int",recGuess_int)
        print("bin recGuess_int",bin(recGuess_int)[2:])
        recGuess_str = zeroExtendLeft(bin(recGuess_int)[2:], expLen+manLen+1)
        recGuess_val = logicFloat_to_float([recGuess_str[0], recGuess_str[1:expLen+1], recGuess_str[expLen+1:]], expLen, manLen)
        print("The latest value of 'recGuess_val' was: " + str(recGuess_val))
        print("-----DEBUG VALUES-----")
        print("\tvalu of 'recGuess' was: " + str(bin(sim.inspect(recGuess))))

    # print("\traw flaot C out: float_C_val_int", bin(float_C_val_int))
    pyOut = rand_flt_a / rand_flt_b
    # print("logfloat rep C:",[float_C_val_str[0], float_C_val_str[1:expLen+1], float_C_val_str[expLen+1:]])
    assert(abs(recGuess_val-pyOut)<1)



