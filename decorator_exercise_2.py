import random
# create a decorator calles chaosmachine
# it replaces all passed values with a random number between 1 and 100
# and then calls the original function

def chaosmachine(func):
    def wrapper(*args, **kwargs):
        zahl = random.random()*100
        result = func(zahl)
        #return func(random.random()*100)
        return result
    return wrapper



@chaosmachine
def double_value(my_number):
    return my_number*2




if __name__ == '__main__':
    print(round(double_value(2)))