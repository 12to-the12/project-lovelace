import time


def testPrime(num):
    if num == 1:
        # 1 is defined as not prime
        return False

    elif num > 1:
        # check for factors
        for i in range(2, num):
            if (num % i) == 0:
                # if factor is found, this is not a prime number
                return False
        # No factors found - number is prime
        return True


@micropython.native
def testPrimeNative(num):
    # No changes to anything below this
    if num == 1:
        # 1 is defined as not prime
        return False

    elif num > 1:
        # check for factors
        for i in range(2, num):
            if (num % i) == 0:
                # if factor is found, this is not a prime number
                return False
        # No factors found - number is prime
        return True


@micropython.viper
def testPrimeViper(num: int) -> bool:
    if num == 1:
        # 1 is defined as not prime
        return False

    elif num > 1:
        # check for factors
        for i in range(2, num):
            if (num % i) == 0:
                # if factor is found, this is not a prime number
                return False
        return True


def compareRunTime(num, funct):
    cpu_frequency = 4.46 * 1e9

    # print("------------")
    # print(f"TESTING whether {num} is prime")
    # print("------------")
    start_time = time.ticks_cpu()
    start = time.time_ns()
    output1 = funct(num)
    end_time = time.ticks_cpu()
    end = time.time_ns()
    cycles = time.ticks_diff(
        end_time, start_time
    )  # How many clock cycles did it take to run the function
    time_s = cycles / cpu_frequency
    time_μs = time_s * 1e6
    # print("{clock}")
    # print(start_time)

    # print(end_time)

    # print(cycles)
    # print(f"Regular script took {time_μs} μs / {cycles} clock cycles")
    print(f"Deduced that {num} is prime:{output1:1} in {(end - start) / 1e6:5.0f} ms")


prime = 4_393_139
compareRunTime(prime, testPrime)  # This is a prime number
compareRunTime(prime, testPrimeNative)  # This is a prime number
compareRunTime(prime, testPrimeViper)  # This is a prime number
