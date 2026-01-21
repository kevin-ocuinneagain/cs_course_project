import time

N = 1000000 # We will change this value

start_time = time.time()

# The core logic you wrote
for i in range(N):
    pass # A simple operation

end_time = time.time()

elapsed_time = end_time - start_time
print(f"Loop of {N} iterations took: {elapsed_time} seconds")