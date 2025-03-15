import random
import time

from collections import OrderedDict

QUERY_TYPES = ("Range", "Update")
ARRAY_SIZE = 100000
QUERY_SIZE = 50000
CACHE_SIZE = 1000

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


def range_sum_no_cache(array: list[int], L: int, R: int) -> int:
    return sum(array[L: R + 1])


def update_no_cache(array: list[int], index: int, value: int) -> int:
    array[index] = value
    return array[index]


def range_sum_with_cache(
    array: list[int],
    L: int,
    R: int,
    cache: LRUCache,
    hits_misses: list[int],
) -> int:
    result = cache.get((L, R))
    if result:
        hits_misses[0] += 1
        return result

    hits_misses[1] += 1
    result = sum(array[L: R + 1])
    cache.put((L, R), result)
    return result


def update_with_cache(array: list[int], index: int, value: int, cache: LRUCache) -> int:
    array[index] = value
    cache.invalidate_range(index)
    return array[index]


def no_cache_processor(array: list[int], queries: list[tuple[str, int, int]]) -> float:
    start_time = time.perf_counter()
    for query in queries:
        if query[0] == "Range":
            range_sum_no_cache(array, query[1], query[2])
        else:
            update_no_cache(array, query[1], query[2])
    return time.perf_counter() - start_time


def cache_processor(
    array: list[int], queries: list[tuple[str, int, int]]
) -> tuple[float, int, int]:
    cache = LRUCache(CACHE_SIZE)
    hits_misses = [0, 0]

    start_time = time.perf_counter()
    for query in queries:
        if query[0] == "Range":
            range_sum_with_cache(
                array, query[1], query[2], cache, hits_misses
            )
        else:
            update_with_cache(array, query[1], query[2], cache)
    return time.perf_counter() - start_time, hits_misses[0], hits_misses[1]


def generate_queries(range_duplicates_ratio: float = .0, updates_ratio: float = .5):
    queries = []
    for _ in range(QUERY_SIZE):
        if random.random() < updates_ratio:
            query_type = "Update"
        elif len(queries) > 10 and random.random() < range_duplicates_ratio:
            query = random.choice(queries)
            while query[0] != "Range":
                query = random.choice(queries)
            queries.append(query)
            continue
        else:
            query_type = "Range"
        first_arg = random.randint(1, ARRAY_SIZE) - 1
        if query_type == "Range":
            second_arg = random.randint(
                first_arg, ARRAY_SIZE - 1)
        else:
            second_arg = random.randint(1, ARRAY_SIZE)
        queries.append((query_type, first_arg, second_arg))
    return queries


if __name__ == "__main__":
    RANGE_DUPLICATES_RATIO = .0
    UPDATES_RATIO = .5

    queries = generate_queries(RANGE_DUPLICATES_RATIO, UPDATES_RATIO)
    array = [random.randint(1, ARRAY_SIZE) for _ in range(ARRAY_SIZE)]
    no_cache_time = no_cache_processor(array, queries)
    print(f"Час виконання без кешування: {no_cache_time} секунд")

    array = [random.randint(1, ARRAY_SIZE) for _ in range(ARRAY_SIZE)]
    cache_time, cache_hits, cache_misses = cache_processor(
        array, queries)

    seen_queries = set()
    repeated = 0
    range_queries = [query for query in queries if query[0] == "Range"]
    for op in range_queries:
        if op[0] == "Range":
            if (op[1], op[2]) in seen_queries:
                repeated += 1
            seen_queries.add((op[1], op[2]))

    print(f"Час виконання з LRU-кешем: {cache_time} секунд")
    print(
        f"Повторювані range запити: {repeated} / {len(range_queries)}")
    print(
        f"Кеш hits: {cache_hits}, Кеш misses: {cache_misses}, Hit Rate: {cache_hits / (cache_hits + cache_misses):.2f}"
    )

    """
    Висновок:
    Використання LRU Cache не є доцільним у даному випадку, оскільки кеш не використовується взагалі.
    Це пов'язано зі складністю ключів та частотою інвалідації внаслідок операцій оновлення.

    Спостереження:
    Ефективність кешу у даній задачі зростає зі зменшенням кількості операцій оновлення
    (UPDATES_RATIO) та збільшенням однакових Range запитів (RANGE_DUPLICATES_RATIO).
    Достатні показники (Cache Hit Rate >30%) можливі тільки при вибірці запитів з дуже низьким відсотком
    оновлень (<1% від загальної кількості операцій) та високим дублюванням Range запитів (>80%).
    """
