import pandas as pd
import matplotlib.pyplot as plt

# Load the CSV file
file_path = 'runtime_data.csv'  # Replace with the path to your CSV file
df = pd.read_csv(file_path, header=None, names=["Timestamp", "Tasks", "Time", "Pi"])

# Split the data into groups
group1 = df.iloc[:4]  # First 5 rows
group2 = df.iloc[4:8]  # Next 3 rows
group3 = df.iloc[8:]   # Last 3 rows

# Plotting
plt.figure(figsize=(10, 6))

# # Group 1
# plt.plot(group1["Tasks"], group1["Time"], marker='o', label="Ray Cluster 2 node")

# # Group 2
# plt.plot(group2["Tasks"], group2["Time"], marker='o', label="Ray Cluster 1 node")

# # Group 3
# plt.plot(group3["Tasks"], group3["Time"], marker='o', label="None Ray")


# Group 1
plt.plot(group1["Tasks"], group1["Pi"], marker='o', label="Ray Cluster 2 node")

# Group 2
plt.plot(group2["Tasks"], group2["Pi"], marker='o', label="Ray Cluster 1 node")

# Group 3
plt.plot(group3["Tasks"], group3["Pi"], marker='o', label="None Ray")

# Logarithmic scale for x-axis due to wide range of task numbers
plt.xscale("log")
plt.xlabel("Number of Tasks (log scale)")
plt.ylabel("Pi Value")
plt.title("Pi Value vs Number of Tasks")
plt.legend()
plt.grid(True, which="both", linestyle="--", linewidth=0.5)
plt.show()
