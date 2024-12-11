import ray
import math
import random
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.patches import Rectangle
NUM_SAMPLING_TASKS = 10
NUM_SAMPLES_PER_TASK = 10_000
TOTAL_NUM_SAMPLES = NUM_SAMPLING_TASKS * NUM_SAMPLES_PER_TASK
ray.init()

@ray.remote
class ProgressActor:
    def __init__(self, total_num_samples: int):
        self.total_num_samples = total_num_samples
        self.num_samples_completed = 0
        self.points_inside_circle = []
        self.points_outside_circle = []

    def report_progress(self, num_samples_completed: int) -> None:
        self.num_samples_completed += num_samples_completed

    def add_points(self, points: list) -> None:
        for x, y, inside_circle in points:
            if inside_circle:
                self.points_inside_circle.append((x, y))
            else:
                self.points_outside_circle.append((x, y))

    def get_progress(self) -> float:
        return self.num_samples_completed / self.total_num_samples

    def get_points(self):
        inside, outside = self.points_inside_circle, self.points_outside_circle
        self.points_inside_circle, self.points_outside_circle = [], []
        return inside, outside

@ray.remote
def sampling_task(num_samples: int, progress_actor: ray.actor.ActorHandle) -> int:
    num_inside = 0
    batch = []
    for _ in range(num_samples):
        x, y = random.uniform(-1, 1), random.uniform(-1, 1)
        inside_circle = math.hypot(x, y) <= 1
        if inside_circle:
            num_inside += 1
        batch.append((x, y, inside_circle))

        # Report progress and batch points every 100,000 samples.
        if len(batch) == 100:
            progress_actor.add_points.remote(batch)
            progress_actor.report_progress.remote(len(batch))
            batch = []
    
    # Report any remaining points
    if batch:
        progress_actor.add_points.remote(batch)
        progress_actor.report_progress.remote(len(batch))
    
    return num_inside


# Create the progress actor
progress_actor = ProgressActor.remote(TOTAL_NUM_SAMPLES)

# Set up the Matplotlib plot
fig, ax = plt.subplots()
ax.set_aspect('equal', 'box')
ax.set_xlim(-1, 1)
ax.set_ylim(-1, 1)

# Plots for points inside and outside the circle
inside_circle_plot, = ax.plot([], [], 'bo', markersize=1)
outside_circle_plot, = ax.plot([], [], 'ro', markersize=1)

# Progress bar setup
progress_text = ax.text(-0.1, 1.05, "Progress: 0%", transform=ax.transAxes, fontsize=10, color='black')

# Placeholder for the final pi estimate text
pi_text = ax.text(0, 1.2, "Calculating...",  fontsize=12, color='purple', ha='center')

def update_plot(frame):
    # Fetch points and progress
    inside_points, outside_points = ray.get(progress_actor.get_points.remote())
    if inside_points:
        x_inside, y_inside = zip(*inside_points)
        inside_circle_plot.set_data(
            list(inside_circle_plot.get_xdata()) + list(x_inside),
            list(inside_circle_plot.get_ydata()) + list(y_inside)
        )
    if outside_points:
        x_outside, y_outside = zip(*outside_points)
        outside_circle_plot.set_data(
            list(outside_circle_plot.get_xdata()) + list(x_outside),
            list(outside_circle_plot.get_ydata()) + list(y_outside)
        )

    # Update progress bar
    progress = ray.get(progress_actor.get_progress.remote())
    progress_text.set_text(f"Progress: {int(progress * 100)}%")

    # Show the estimated Pi value when progress completes
    if progress >= 1.0:
        total_num_inside = sum(ray.get(results))
        pi_estimate = (total_num_inside * 4) / TOTAL_NUM_SAMPLES
        pi_text.set_text(f"Estimated value of π: {pi_estimate:.5f}")
        plt.draw()
        ani.event_source.stop()  # Stop the animation

    return inside_circle_plot, outside_circle_plot, progress_text, pi_text

# Create and execute all sampling tasks in parallel
results = [
    sampling_task.remote(NUM_SAMPLES_PER_TASK, progress_actor)
    for _ in range(NUM_SAMPLING_TASKS)
]

# Run the dynamic plot
ani = FuncAnimation(fig, update_plot, interval=5)

# Start plot
plt.show()
ray.shutdown()
