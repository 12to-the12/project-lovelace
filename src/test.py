import threading
from time import sleep

def myfunction(subject):
    for _ in range(10):
        print(f"{subject}")
        sleep(0.1)


if __name__=="__main__":
    mythread = threading.Thread(target=myfunction,args=("A",))
    mythread.start()

    mythreadb = threading.Thread(target=myfunction,args=("B",))
    mythreadb.start()

    mythreadc = threading.Thread(target=myfunction,args=("C",))
    mythreadc.start()