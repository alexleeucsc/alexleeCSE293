import pyrtl
from math import pow
pyrtl.reset_working_block()

# state enums
WAITING, MULTIPLYING = [pyrtl.Const(x, bitwidth=2) for x in range(2)]

aReg = pyrtl.Register(6, 'aReg')
bReg = pyrtl.Register(6, 'bReg')
cReg = pyrtl.Register(12, 'cReg')
ready_ab_reg = pyrtl.Register(1, 'ready_ab_reg')
valid_c_reg = pyrtl.Register(1, 'valid_c_reg')
mult_state = pyrtl.Register(1, 'mult_state')

def shift_mult(a, b, c, ready_ab, valid_ab, ready_c, valid_c, digitMask):
    #if an input is ready, then aReg and bReg will be reset
    # aReg = pyrtl.Register(6, 'aReg')
    # bReg = pyrtl.Register(6, 'bReg')
    # cReg = pyrtl.Register(12, 'cReg')
    # ready_ab_reg = pyrtl.Register(1, 'ready_ab_reg')
    # valid_c_reg = pyrtl.Register(1, 'valid_c_reg')
    # mult_state = pyrtl.Register(1, 'mult_state')
    c <<= cReg
    ready_ab <<= ready_ab_reg
    valid_c <<= valid_c_reg
    with pyrtl.conditional_assignment:
        with mult_state == WAITING:
            #with ready_ab == pyrtl.Const("1'b1") and valid_ab == pyrtl.Const("1'b1"):
            with (ready_ab_reg == pyrtl.Const("1'b1")) & (valid_ab == pyrtl.Const("1'b1")):
                mult_state.next |= MULTIPLYING
                digitMask.next |= pyrtl.Const("6'b111111")
                aReg.next |= a
                bReg.next |= b
                ready_ab_reg.next |= pyrtl.Const("1'b0")
        with mult_state == MULTIPLYING:
            with (digitMask & bReg) > 0:
                digitMask.next |= digitMask * 2
                #cReg |= cReg + (a * )
                with bReg[0] == 1:
                    cReg.next |= cReg + (aReg)
                aReg.next |= aReg*2
                bReg.next |= pyrtl.shift_right_arithmetic(bReg,1)
                valid_c_reg.next |= pyrtl.Const("1'b0")
            with (digitMask & bReg) == 0:
                with ~((ready_c == pyrtl.Const("1'b1")) & (valid_c_reg == pyrtl.Const("1'b1"))): 
                    digitMask.next |= pyrtl.Const("6'b111111")
                    valid_c_reg.next |= pyrtl.Const("1'b1")
                with (ready_c == pyrtl.Const("1'b1")) & (valid_c_reg == pyrtl.Const("1'b1")): 
                    mult_state.next |= WAITING
                    #digitMask.next |= pyrtl.Const("6'b111111")
                    aReg.next |= a
                    bReg.next |= b
                    ready_ab_reg.next |= pyrtl.Const("1'b1")
                    valid_c_reg.next |= pyrtl.Const("1'b0")

#inputs
a = pyrtl.Input(6, 'a')
b = pyrtl.Input(6, 'b')
valid_ab = pyrtl.Input(1, 'valid_ab')
ready_c = pyrtl.Input(1, 'ready_c')
#outputs
c = pyrtl.Output(6, 'c')
valid_c = pyrtl.Output(1, 'valid_c')
ready_ab = pyrtl.Output(1, 'ready_ab')

digitMask = pyrtl.Register(6, 'digitMask')


shift_mult(a, b, c, ready_ab, valid_ab, ready_c, valid_c, digitMask)

#sim_trace = pyrtl.SimulationTrace(register_value_map={digitMask: "6'b111111"})
sim_trace = pyrtl.SimulationTrace()
#bug 051523: https://pyrtl.readthedocs.io/en/latest/simtest.html
# register_value_map has format {reg:int}
sim = pyrtl.Simulation(tracer=sim_trace, register_value_map={   digitMask: int(pow(2,6))-1,
                                                                mult_state: 0,
                                                                ready_ab_reg: 1,})


for cycle in range(2):
    sim.step({
        'a': 5,
        'b': 3,
        'valid_ab':1,
        'ready_c':0,
    })
for cycle in range(5):
    sim.step({
        'a': 0,
        'b': 0,
        'valid_ab':1,
        'ready_c':0,
    })

print('--- Simulation ---')
sim_trace.render_trace(symbol_len=5, segment_size=5)

c_value = sim.inspect(c)
print("The latest value of 'c' was: " + str(c_value))