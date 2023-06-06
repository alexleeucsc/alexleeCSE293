import pyrtl
from fplib import *
from math import pow
import random
pyrtl.reset_working_block()

#params

# state enums
WAITING, MULTIPLYING = [pyrtl.Const(x, bitwidth=2) for x in range(2)]


# ready_ab_reg = pyrtl.Register(1, 'ready_ab_reg')
# valid_c_reg = pyrtl.Register(1, 'valid_c_reg')
# mult_state = pyrtl.Register(1, 'mult_state')

expLen=8
manLen=16
#inputs
float_A = pyrtl.Input(expLen+manLen+1, 'float_A')
float_B = pyrtl.Input(expLen+manLen+1, 'float_B')
#outputs
float_C = pyrtl.Output(expLen+manLen+1, 'float_C')

class multTestClass:
    def __init__(self, nameTag, expLen=8, manLen=16):
        self.expLen = expLen
        self.manLen = manLen
        #wires
        self.signA = pyrtl.WireVector(1, 'signA'+nameTag)
        self.expA = pyrtl.WireVector(self.expLen, 'expA'+nameTag)
        self.manA = pyrtl.WireVector(self.manLen, 'manA'+nameTag)
        self.signB = pyrtl.WireVector(1, 'signB'+nameTag)
        self.expB = pyrtl.WireVector(self.expLen, 'expB'+nameTag)
        self.manB = pyrtl.WireVector(self.manLen, 'manB'+nameTag)
        self.signC = pyrtl.WireVector(1, 'signC'+nameTag)
        #debugWires
        self.manCLongWire = pyrtl.WireVector(2+self.manLen*2, 'manCLongWire'+nameTag)
        self.manCLongWireCut = pyrtl.WireVector(1+self.manLen, 'manCLongWireCut'+nameTag)
        self.expCDebug = pyrtl.WireVector(self.expLen+1, 'expCDebug'+nameTag)
        self.manCLongDeciderDebug = pyrtl.WireVector(1, 'manCLongDeciderDebug'+nameTag)
    def multiplyLogicFloat(self,float_A, float_B, float_C):
        self.signA <<= float_A[self.expLen+self.manLen]
        self.expA <<= float_A[self.manLen:self.expLen+self.manLen]
        self.manA <<= float_A[:self.manLen]
        self.signB <<= float_B[self.expLen+self.manLen]
        self.expB <<= float_B[self.manLen:self.expLen+self.manLen]
        self.manB <<= float_B[:self.manLen]
        #with pyrtl.conditional_assignment:
        print("binary string:",str(self.expLen)+"'b1"+('0'*(self.expLen-1)))
        expC = self.expA+self.expB-pyrtl.Const(str(self.expLen)+"'b1"+('0'*(self.expLen-1)))
        self.expCDebug <<= expC
        #multiply manC, shift right until first bit is a 1
        manCLong = pyrtl.concat(pyrtl.Const("1'b1"), self.manA) * pyrtl.concat(pyrtl.Const("1'b1"), self.manB)
        print("@@@@@",len(manCLong),"@@@@@")
        self.manCLongWireCut <<= pyrtl.concat(pyrtl.Const("1'b1"), self.manA) * pyrtl.concat(pyrtl.Const("1'b1"), self.manB)
        self.manCLongWire <<= manCLong[len(manCLong)-self.manLen-2:-2]
        self.manCLongDeciderDebug <<= manCLong[-1]
        # with manCLong[-1] == pyrtl.Const("1'b1"):
        #     #BUG 052923 - manCLong bit index wrong, should be -1
        #     #BUG 052923 - the -1 and -2 were mixed
        #     #BUG 052923 - add one to exp when first bit is a 1 and you are cutting off less
        #     float_C |= pyrtl.concat_list([manCLong[len(manCLong)-self.manLen-1:-1], (self.expA+self.expB-pyrtl.Const(str(self.expLen)+"'b1"+('0'*(self.expLen-1))))+1, pyrtl.Const("1'b0")])
        # with manCLong[-1] == pyrtl.Const("1'b0"):
        #     float_C |= pyrtl.concat_list([manCLong[len(manCLong)-self.manLen-2:-2], (self.expA+self.expB-pyrtl.Const(str(self.expLen)+"'b1"+('0'*(self.expLen-1)))), pyrtl.Const("1'b0")])
            #float_C |= pyrtl.concat_list([manCLong[1:1+self.expLen], (expA+expB-pyrtl.Const(str(self.expLen)+"'b1"+('0'*(self.expLen-1))))[self.expLen], signA^signB])
        self.signC <<= self.signA ^ self.signB
        float_C <<= pyrtl.select(manCLong[-1] == pyrtl.Const("1'b1"),
        pyrtl.concat_list(  [
                            manCLong[len(manCLong)-self.manLen-1:-1],
                            ( (self.expA+self.expB-pyrtl.Const(str(self.expLen)+"'b1"+('0'*(self.expLen-1))))+1 )[:-3],
                            #pyrtl.Const("1'b0")
                            #self.signA ^ self.signB
                            self.signC
                            ]),
        pyrtl.concat_list(  [
                            manCLong[len(manCLong)-self.manLen-2:-2],
                            (self.expA+self.expB-pyrtl.Const(str(self.expLen)+"'b1"+('0'*(self.expLen-1))))[:-2],
                            #pyrtl.Const("1'b0")
                            #self.signA ^ self.signB
                            self.signC
                            ]))
        # valid_c_reg <<= pyrtl.Const("1'b1")
        # mult_state <<= pyrtl.Const("1'b1")

if __name__ == "__main__":

    multTestObj = multTestClass("obj1", expLen, manLen)
    multTestObj.multiplyLogicFloat(float_A, float_B, float_C)

    #sim_trace = pyrtl.SimulationTrace(register_value_map={digitMask: "6'b111111"})
    sim_trace = pyrtl.SimulationTrace()
    #bug 051523: https://pyrtl.readthedocs.io/en/latest/simtest.html
    # register_value_map has format {reg:int}
    sim = pyrtl.Simulation(tracer=sim_trace, register_value_map={   #digitMask: int(pow(2,6))-1,
                                                                    #mult_state: 0,
                                                                    #ready_ab_reg: 1,
                                                                })
    for cycle in range(10000):
        rand_flt_a = random.uniform(0.001,pow(2,5))
        rand_flt_b = random.uniform(0.001,pow(2,5))
        a_sign = random.choice([1,-1])
        b_sign = random.choice([1,-1])
        rand_flt_a = rand_flt_a * a_sign
        rand_flt_b = rand_flt_b * b_sign
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
        strValA = ''.join(logicValA)
        strValB = ''.join(logicValB)
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
        print("\traw flaot C out: float_C_val", float_C_val)
        pyOut = rand_flt_a * rand_flt_b
        print("logfloat rep C:",[float_C_val_str[0], float_C_val_str[1:expLen+1], float_C_val_str[expLen+1:]])
        assert(abs(float_C_val-pyOut)<1)


    print('--- Simulation ---')
    sim_trace.render_trace(symbol_len=5, segment_size=5)

    c_value = sim.inspect(float_C)
    print("The latest value of 'c' was: " + str(c_value))