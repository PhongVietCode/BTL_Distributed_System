import random
import math
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

# Dictionary to track progress of each task
num_samples_completed_per_task = {}

# Function to estimate points inside the circle for Pi calculation
def sampling_task(num_samples: int, task_id: int) -> int:
    num_inside = 0
    for i in range(num_samples):
        x, y = random.uniform(-1, 1), random.uniform(-1, 1)
        if math.hypot(x, y) <= 1:
            num_inside += 1

        # Update progress every 1 million samples
        if (i + 1) % 1_000_000 == 0:
            num_samples_completed_per_task[task_id] = i + 1

    num_samples_completed_per_task[task_id] = num_samples
    return num_inside

# Main configuration
NUM_SAMPLING_TASKS = 10
NUM_SAMPLES_PER_TASK = 100_000_000  # Reduced for demo purposes
TOTAL_NUM_SAMPLES = NUM_SAMPLING_TASKS * NUM_SAMPLES_PER_TASK

print("Time started")
start_time = time.time()
points_in = 0

# Create ThreadPoolExecutor to run tasks concurrently
with ThreadPoolExecutor(max_workers=NUM_SAMPLING_TASKS) as executor:
    # Submit tasks to the executor
    futures = {executor.submit(sampling_task, NUM_SAMPLES_PER_TASK, i): i for i in range(NUM_SAMPLING_TASKS)}

    # Query progress periodically and accumulate results as tasks complete
    for future in as_completed(futures):
        task_id = futures[future]
        result = future.result()
        points_in += result
        # Print overall progress by summing completed samples
        print(f"Progress: {sum(num_samples_completed_per_task.values()) / TOTAL_NUM_SAMPLES:.2%}")

# Calculate Pi based on accumulated points
pi = (points_in * 4) / TOTAL_NUM_SAMPLES
print(f"Estimated value of π is: {pi}")
print(f"Execute time: {time.time() - start_time:.2f} seconds")
