import threading

print_lock = threading.Lock()
p = print


def print(*a, **b):
    with print_lock:
        p(*a, **b)


total_lock = threading.Lock()
total = 0


def updtotal():
    global total
    with total_lock:
        total += 1
        return total


def reset_total():
    global total
    with total_lock:
        total = 0
        return total


def get_total():
    return total
