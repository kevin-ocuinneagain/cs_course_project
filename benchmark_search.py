import random
import string
import time

def quick_sort_contacts(items):
    if len(items) <= 1:
        return items

    pivot = items[len(items) // 2]
    pivot_name = pivot['name'].lower()

    left = []
    middle = []
    right = []

    for item in items:
        name = item['name'].lower()
        if name < pivot_name:
            left.append(item)
        elif name > pivot_name:
            right.append(item)
        else:
            middle.append(item)

    return quick_sort_contacts(left) + middle + quick_sort_contacts(right)

def linear_search(items, name):
    target = name.lower()
    for item in items:
        if item['name'].lower() == target:
            return item
    return None

def binary_search_contact(items, name):
    low = 0
    high = len(items) - 1
    target = name.lower()

    while low <= high:
        mid = (low + high) // 2
        mid_name = items[mid]['name'].lower()

        if mid_name == target:
            return items[mid]
        elif mid_name < target:
            low = mid + 1
        else:
            high = mid - 1

    return None

def random_name():
    return ''.join(random.choices(string.ascii_letters, k=8))

contacts = []
for i in range(10000):
    contacts.append({
        'name': random_name() + str(i),
        'email': f'user{i}@example.com'
    })

target_contact = contacts[-1]
target_name = target_contact['name']

sorted_contacts = quick_sort_contacts(contacts)

start = time.perf_counter()
for _ in range(1000):
    linear_search(contacts, target_name)
linear_time = time.perf_counter() - start

start = time.perf_counter()
for _ in range(1000):
    binary_search_contact(sorted_contacts, target_name)
binary_time = time.perf_counter() - start

print("Linear Search time:", linear_time)
print("Binary Search time:", binary_time)

if binary_time > 0:
    print("Binary Search was about", linear_time / binary_time, "times faster")