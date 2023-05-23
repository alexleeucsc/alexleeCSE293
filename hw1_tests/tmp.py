def float_to_Logicfloat(floatIn, expLen, manLen):
    whole,frac = int(floatIn), floatIn - int(floatIn)
    mantWhole,mantFrac = bin(whole)[2:] if whole>0 else '', ''
    #exp = pow(2,expLen-1) #BUG 052023 - exp should start at bias!
    #while len(mantFrac)+len(mantWhole) < manLen+1 and exp>0  and frac != 0:
    while len(mantFrac)+len(mantWhole) < manLen+1 and frac != 0:
        print(frac)
        frac = frac * 2
        mantFrac += ('1' if frac > 1 else '0')
        frac -= 1 if frac > 1 else 0
        #print(exp, bin(exp))
    if whole>0:
        exp = len(bin(whole)[2:])-1
    else:
        exp = (-1*mantFrac.index('1'))-1
    exp = exp + pow(2,expLen-1)
    assert(mantWhole=='' or mantWhole[0]=='1')
    return ['1' if floatIn<0 else '0', bin(exp)[2:], (mantWhole+mantFrac)[1:]]
#float_to_Logicfloat(0.0013150890585834638, 28, 8)


#52123
import pyrtl

# "pin" input/outputs
a = pyrtl.Input(8, 'a')
b = pyrtl.Input(8, 'b')
q = pyrtl.Output(16, 'q')
gt5 = pyrtl.Output(1, 'gt5')

sum = a * b  # makes an 8-bit adder
q <<= sum  # assigns output of adder to out pin
gt5 <<= sum > 5  # does a comparison, assigns that to different pin

# the simulation and waveform output
sim = pyrtl.Simulation()
sim.step_multiple({'a': [0, 1, 2, 3, 4], 'b': [2, 2, 3, 3, 4]})
sim.tracer.render_trace()
