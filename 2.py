from functools import lru_cache, partial
from timeit import timeit

import matplotlib.pyplot as plt

from splaytree import SplayTree

@lru_cache(maxsize=10)
def fibonacci_lru(n: int) -> int:
    if n < 2:
        return n
    return fibonacci_lru(n - 1) + fibonacci_lru(n - 2)

def fibonacci_splay(n: int, tree: SplayTree) -> int:
    if n < 2:
        return n
    result = tree.find(n)
    if result:
        return result.value
    result = fibonacci_splay(n - 1, tree) + fibonacci_splay(n - 2, tree)
    tree.insert(n, result)
    return result

def graphics(n_values: list[int], lru_times: list[float], splay_times: list[float]):
    plt.figure(figsize=(10, 6))
    plt.plot(n_values, lru_times, marker='o', linestyle='-', label="LRU Cache")
    plt.plot(n_values, splay_times, marker='x', linestyle='-', label="Splay Tree", color="orange")

    plt.xlabel("Число Фібоначчі (n)")
    plt.ylabel("Середній час виконання (секунди)")
    plt.title("Порівняння часу виконання для LRU Cache та Splay Tree")

    plt.grid(True)

    plt.legend()

    plt.show()

if __name__ == "__main__":
    n_values = [i * 50 for i in range(0, 20)]

    tree = SplayTree()

    lru_times = []
    for n in n_values:
        lru_times.append(timeit(partial(fibonacci_lru, n), number=1))

    splay_times = []
    for n in n_values:
        splay_times.append(timeit(partial(fibonacci_splay, n, tree), number=1))

    # Results table
    print(f"{'n':<10} {'LRU Cache Time (s)':<20} {'Splay Tree Time (s)':<20}")
    print("-" * 60)
    for n, lru, splay in zip(n_values, lru_times, splay_times):
        print(f"{n:<10} {lru:<20.8f} {splay:<20.8f}")

    graphics(n_values, lru_times, splay_times)

    """
    Висновок:
    LRU Cache є значно ефективнішим для обчислення чисел Фібоначчі на великих значеннях n, аніж
    SplayTree.

    Спостереження:
    1. LRU показує стабільно низький час виконання, a Splay Tree різко збільшує час виконання вже
    після перших ітерацій, і є нестабільним при великих n.
    2. Використання LRU Cache дозволяє уникнути зайвих обчислень, завдяки кешуванню. В той час як
    Splay Tree виконуючи ту саму функцію, має додаткові операції перебалансування при частих
    доступах до вузлів.
    """