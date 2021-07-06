import time

def timer(func,*args,**kwargs):
    def wrapper(*args,**kwargs):
        start = time.time()
        result = func(*args,**kwargs)
        print(f'Time spend in {func.__name__} :{round(time.time()-start,3)} seconds')
        return result
    return wrapper
