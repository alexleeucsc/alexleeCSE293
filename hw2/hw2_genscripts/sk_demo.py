def bk_demo(values, operator):
    print(values)
    if len(values)>1:
        left = bk_demo(values[:int(len(values)/2)], operator)
        right = bk_demo(values[int(len(values)/2):], operator)
        return left + [operator(left[-1], item) for item in right]
    else:
        return values


values = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15]
operator = lambda x,y:x+y
out = bk_demo(values, operator)
print(out)