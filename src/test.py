import gzip


def another():
    return 5


def default_tester(x=another()):
    print(x)


if __name__ == "__main__":
    default_tester(7)
    default_tester()
