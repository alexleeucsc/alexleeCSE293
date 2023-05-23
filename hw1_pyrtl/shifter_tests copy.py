import pyrtl
from math import pow
pyrtl.reset_working_block()

#params
expLen = 8
manLen = 64

# state enums
WAITING, MULTIPLYING = [pyrtl.Const(x, bitwidth=2) for x in range(2)]

aReg = pyrtl.Register(6, 'aReg')

ready_ab_reg = pyrtl.Register(1, 'ready_ab_reg')
valid_c_reg = pyrtl.Register(1, 'valid_c_reg')
mult_state = pyrtl.Register(1, 'mult_state')

#inputs
float_A = pyrtl.Input(6, 'a')
float_B = pyrtl.Input(6, 'b')
valid_ab = pyrtl.Input(1, 'valid_ab')
ready_c = pyrtl.Input(1, 'ready_c')
#outputs
c = pyrtl.Output(6, 'c')
valid_c = pyrtl.Output(1, 'valid_c')
ready_ab = pyrtl.Output(1, 'ready_ab')


shift_mult(float_A, float_C, eady_ab, valid_ab, ready_c, valid_c, digitMask)

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