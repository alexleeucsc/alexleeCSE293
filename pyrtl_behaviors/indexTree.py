# PyRTL does something pretty cool; if you write
# newWireName = wire OP wire
# it automatically creates a new wire called "newWireName"
# in conditionalAssignb, shiftRightAmountRev is created on the fly
# the problem is that wires created on the fly cannot be conditionally assigned
# here, we will show that when "shiftRightAmountRev" is explicitly enumerated as a wire,
# it can be conditionally assigned, but when it isn't,
# shiftRightAmountRev follows "last assignment" semantics

from pyrtl import *
from fplib import *
from math import pow
import random
from providedLib import prioritized_mux
reset_working_block()

#inputs
inputArr = Input(10, 'inputArr')
vals = [Const(i) for i in range(10)]

priority = pyrtl.WireVector(64, 'priority')

priority <<= prioritized_mux(inputArr, vals)

sim_trace = SimulationTrace()
sim = Simulation(tracer=sim_trace, register_value_map={})


for cycle in range(1):
    sim.step({
        'inputArr': int("0000001011", 2),
    })
    print("\tvalu of 'priority' was: " + str(bin(sim.inspect(priority))))


print('--- Simulation ---')
sim_trace.render_trace(symbol_len=5, segment_size=5)