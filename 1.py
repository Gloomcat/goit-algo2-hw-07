import random

from collections import OrderedDict
from functools import partial
from timeit import timeit


class LRUCache:
    def __init__(self, capacity):
        self.cache = OrderedDict()
        self.capacity = capacity

    def get(self, key):
        if key in self.cache:
            self.cache.move_to_end(key)
            return self.cache[key]
        return None

    def put(self, key, value):
        if key in self.cache:
            self.cache.move_to_end(key)
        elif len(self.cache) >= self.capacity:
            self.cache.popitem(last=False)
        self.cache[key] = value

    def invalidate_range(self, index):
        keys_to_remove = [key for key in self.cache if key[0] <= index <= key[1]]
        for key in keys_to_remove:
            del self.cache[key]


cache = LRUCache(1000)


def range_sum_no_cache(array: list[int], L: int, R: int) -> int:
    return sum(array[L:R+1])

def update_no_cache(array: list[int], index: int, value: int) -> int:
    array[index] = value
    return array[index]

def range_sum_with_cache(array: list[int], L: int, R: int) -> int:
    result = cache.get((L, R))
    if result:
        return result

    result = sum(array[L:R+1])
    cache.put((L, R), result)
    return result

def update_with_cache(array: list[int], index: int, value: int) -> int:
    array[index] = value
    cache.invalidate_range(index)
    return array[index]

handlers_no_cache = {
    "Range": range_sum_no_cache,
    "Update": update_no_cache
}

handlers_with_cache = {
    "Range": range_sum_with_cache,
    "Update": update_with_cache
}

def executor(array: list[int], operations: list[tuple[str, int, int]], cache: bool) -> None:
    if cache:
        range_sum = range_sum_with_cache
        updater = update_with_cache
    else:
        range_sum = range_sum_no_cache
        updater = update_no_cache

    step = int(len(operations) / 100)
    for index, operation in enumerate(operations):
        if index % step == 0:
            print(f"{"Cache" if cache else "No cache"} progress: {index // step}%")
        if operation[0] == "Range":
            range_sum(array, operation[1], operation[2])
        else:
            updater(array, operation[1], operation[2])


if __name__ == "__main__":
    operation_types = ("Range", "Update")
    array_size = 100000
    operation_size = 50000

    array = [random.randint(1, array_size) for _ in range(array_size)]
    operations = []
    for _ in range(operation_size):
        operation_type = random.choice(operation_types)
        first_arg = random.randint(1, array_size) - 1
        if operation_type == "Range":
            second_arg = random.randint(first_arg, array_size - 1)
        else:
            second_arg = random.randint(1, array_size)
        operations.append((operation_type, first_arg, second_arg))

    no_cache_time = timeit(
        partial(executor, array, operations, False), number=1)
    with_cache_time = timeit(
        partial(executor, array, operations, True), number=1)

    print(f"Час виконання без кешування: {no_cache_time} секунд")
    print(f"Час виконання з LRU-кешем: {with_cache_time} секунд")

    """
    Результат:
    Час виконання майже однаковий в обох випадках. Використання кешу займає дещо більше часу.

    Спостереження:
    1. Операція суми виконується швидко.
    2. Кеш метод get() з ключами типу (L, R) має низьку ймовірність hit-a.
    3. Операції з кешем - додають час виконання.

    Висновок:
    У даному прикладі використання кешу не є доцільним. Кешування буде ефективнішим при
    виконанні складних операцій з даними, що потребуватимуть більше часу і/або використанні
    простіших ключів, що збільшить ймовірність hit-a.
    """
