import ray
import math
import time
import random
import csv
ray.init()

@ray.remote
class ProgressActor:
    def __init__(self, total_num_samples: int):
        self.total_num_samples = total_num_samples
        self.num_samples_completed_per_task = {}

    def report_progress(self, task_id: int, num_samples_completed: int) -> None:
        self.num_samples_completed_per_task[task_id] = num_samples_completed

    def get_progress(self) -> float:
        return (
            sum(self.num_samples_completed_per_task.values()) / self.total_num_samples
        )
        
@ray.remote
def sampling_task(num_samples: int, task_id: int,
                  progress_actor: ray.actor.ActorHandle) -> int:
    num_inside = 0
    for i in range(num_samples):
        x, y = random.uniform(-1, 1), random.uniform(-1, 1)
        if math.hypot(x, y) <= 1:
            num_inside += 1

        # Report progress every 1 million samples.
        if (i + 1) % 1_000_000 == 0:
            # This is async.
            progress_actor.report_progress.remote(task_id, i + 1)

    progress_actor.report_progress.remote(task_id, num_samples)
    return num_inside


i = 1
while i < 4:
    print(f"Start test - {i}")
    # Change this to match your cluster scale.
    NUM_SAMPLING_TASKS = pow(10, i)
    NUM_SAMPLES_PER_TASK = 10_000_000
    TOTAL_NUM_SAMPLES = NUM_SAMPLING_TASKS * NUM_SAMPLES_PER_TASK

    # Create the progress actor.
    progress_actor = ProgressActor.remote(TOTAL_NUM_SAMPLES)
    # Create and execute all sampling tasks in parallel.
    results = [
        sampling_task.remote(NUM_SAMPLES_PER_TASK, i, progress_actor)
        for i in range(NUM_SAMPLING_TASKS)
    ]
    start_time = time.time()
    # Query progress periodically.
    while True:
        progress = ray.get(progress_actor.get_progress.remote())
        print(f"Progress: {int(progress * 100)}%")

        if progress == 1:
            break

        time.sleep(1)
    # Get all the sampling tasks results.
    total_num_inside = sum(ray.get(results))
    pi = (total_num_inside * 4) / TOTAL_NUM_SAMPLES
    # print(f"Estimated value of π is: {pi}")
    runtime = time.time() - start_time
    # print(f"Execute time: {runtime}")


    with open('runtime_data.csv', 'a', newline='') as file:
        writer = csv.writer(file)
        # Save timestamp, runtime, process name, and result value
        writer.writerow([time.strftime("%Y-%m-%d %H:%M:%S"), runtime, pi])
    print(f"Done-{i}")
    i = i + 1

    
ray.shutdown()