
import math

#part 1 logical mdoels: multiplier


#part 2 logical models
#the formula for this are taken from the wikipedia entry:
#@https://en.wikipedia.org/wiki/Division_algorithm#Newton%E2%80%93Raphson_division
def nr_logical(num,div,rep=10):
    e = (pow(2,int(math.log(div,2)+1)))
    print("pow of 2 normalizing factor:", e)
    num = num / e
    div = div / e
    print(div)
    rec_guess = (48/17)-(32/17)*div
    for _ in range(rep):
        print("new guess for reciprocol:",rec_guess)
        rec_guess = rec_guess + rec_guess*(1-(div*rec_guess))
    return num*rec_guess
print(nr_logical(121,11))