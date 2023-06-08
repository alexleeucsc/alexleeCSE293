
import math
import random
def nr_logical(num,div,rep=10):
    #normalize the inputs
    e = (pow(2,int(math.log(div,2)+1)))
    print("pow of 2 normalizing factor:", e)
    num = num / e
    div = div / e
    print(num, div)
    #get an initial guess
    rec_guess = (48/17)-(32/17)*div
    for _ in range(rep):
        #update the guess
        print("\tnew guess for reciprocol:",rec_guess)
        print("\tdiv*rec_guess",div*rec_guess)
        print("\t(1-(div*rec_guess))",(1-(div*rec_guess)))
        print("\trec_guess*(1-(div*rec_guess))",rec_guess*(1-(div*rec_guess)))
        rec_guess = rec_guess + rec_guess*(1-(div*rec_guess))
    return num*rec_guess
print(nr_logical(43,7))

