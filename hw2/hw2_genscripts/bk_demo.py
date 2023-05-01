import math
def nextAccumArr_forward(values, level, operator):
    next_values = [values[i] for i in range(len(values))]
    operationCount = int(len(values)/(pow(2,level+1)))
    for i in range(operationCount):
        next_values[((i+1)*pow(2,level+1))-1] = operator(values[((i+1)*pow(2,level+1))-1], values[((i+1)*pow(2,level+1))-1-pow(2,level)])
    return next_values

def nextAccumArr_backward(values, level, operator):
    next_values = [values[i] for i in range(len(values))]
    operationCount = pow(2,level+1)-1
    for i in range(operationCount):
        # split_idx = ((i+1)*(int(len(values)/(pow(2,level+1)))))-1
        stride = int(len(values)/pow(2,level+1))
        split_idx = (stride*(i+1))-1
        half_stride = int(stride/2)
        next_values[split_idx+half_stride] = operator(values[split_idx+half_stride], values[split_idx])
    return next_values

def bk_demo(values, operator):
    for level in range(int(math.log(len(values),2))):
        values = nextAccumArr_forward(values,level,operator)
        print(values)
    print("-----")
    for level in range(int(math.log(len(values),2))-1):
        values = nextAccumArr_backward(values,level,operator)
        print(values)

values = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15]
operator = lambda x,y:x+y
bk_demo(values,operator)
