import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import savgol_filter
from sklearn.neighbors import LocalOutlierFactor
import os
import re


#%% Directory where CSVs are stored
root_folder = "Results/"


# for file in os.listdir(root_folder):
#     if file.endswith(".csv"):
#         print(file)
file = "EtAc_10-2_AIR_0_Red_150uWcm2_0_p1_1_SSeChR_2025-07-04_16-52-21_F_D_raw.csv"   #For a single experiment csv file only
file_path = os.path.join(root_folder, file)
"""
1) Median-filter X/Y and show raw vs median.
2) Savitzky-Golay smooth the median-filtered X/Y.
3) Compute displacement, speed, acceleration from the smoothed traces.
4) Plot Displacement, Speed, and Acceleration (with event markers).

Parameters:
    - file_path: path to CSV (with header on line skip_rows+1)
    - skip_rows: metadata lines before header
    - med_kernel: odd window for median filter
    - sg_window: odd window for Savitzky–Golay filter
    - sg_poly: polynomial order for S‑G (< sg_window)
"""
# ── 1) LOAD & CLEAN ───────────────────────────────────────────────────
df = pd.read_csv(file_path, skiprows=1)
df = df.dropna(subset=["Time_stamp", "Larva_centroid_X", "Larva_centroid_Y"])
df["Time_stamp"] = pd.to_numeric(df["Time_stamp"], errors="coerce")
df = df.dropna(subset=["Time_stamp"]).reset_index(drop=True)

# floats for filter
df["X_raw"] = df["Larva_centroid_X"].astype(float)
df["Y_raw"] = -df["Larva_centroid_Y"].astype(float)


# Plot raw X/Y

# # Plot X vs Y
# plt.figure(figsize=(8, 6))
# plt.scatter(df["X_raw"], df["Y_raw"], c='blue', s=10, alpha=0.7)
# plt.xlabel("X Position")
# plt.ylabel("Y Position")
# plt.title("Larva Raw X/Y Scatter Plot")
# plt.grid(True)
# plt.axis('equal')  # Optional: keeps X and Y scaling uniform
# plt.show()


#%%
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from sklearn.neighbors import LocalOutlierFactor
from sklearn.ensemble import IsolationForest
from sklearn.svm import OneClassSVM

# Prepare data
XY_points = df[["X_raw", "Y_raw"]].values

# Initialize models
lof = LocalOutlierFactor(n_neighbors=20, contamination=0.03)
isf = IsolationForest(contamination=0.03, random_state=42)

isf = IsolationForest(
    n_estimators=500,          # More trees = smoother, more stable result
    max_samples='auto',        # Uses all data for each tree by default
    contamination=0.02,        # Assumes 2% of data are outliers (adjust if needed)
    max_features=1.0,         # Use all features (X and Y)
    bootstrap=False,          # Standard random forests, no bootstrap sampling
    random_state=42
)



ocsvm = OneClassSVM(kernel='rbf', gamma='auto', nu=0.03)

# Fit models & predict

df["IF_pred"] = isf.fit_predict(XY_points)

plt.figure(figsize=(7, 5))

# split inliers vs outliers
inliers  = df[df["IF_pred"] == 1]
outliers = df[df["IF_pred"] == -1]

# plot retained points
plt.scatter(
    inliers["X_raw"], inliers["Y_raw"],
    c='blue', s=10, alpha=0.7,
    label='Retained (inliers)'
)

# plot isolated points
plt.scatter(
    outliers["X_raw"], outliers["Y_raw"],
    c='red', s=10, alpha=0.7,
    label='Isolated (outliers)'
)

plt.title("Isolation Forest Outlier Detection on Raw X/Y Data")
plt.xlabel("X Position")
plt.ylabel("Y Position")
plt.axis('equal')
plt.legend(loc='best')
plt.tight_layout()

plt.savefig("Isolation_Forest.svg", format="svg")
plt.show()




#%%
# Create mask for inliers
mask_inliers = df["IF_pred"] == 1

# Masked arrays
x_masked = df["X_raw"].copy()
y_masked = df["Y_raw"].copy()

# Optional: Replace outliers with NaN
x_masked[~mask_inliers] = np.nan
y_masked[~mask_inliers] = np.nan

# Interpolate NaNs (optional but helps smoothing)
x_masked = pd.Series(x_masked).interpolate(limit_direction='both').values
y_masked = pd.Series(y_masked).interpolate(limit_direction='both').values

# Recalculate filter parameters
n = len(x_masked)


sg_window=100
sg_poly=2

if sg_window % 2 == 0: sg_window += 1
if sg_window > n: sg_window = n//2*2 - 1
if sg_poly >= sg_window: sg_poly = sg_window - 1

# Apply Savitzky–Golay across full sequence
x_sg_full = savgol_filter(x_masked, sg_window, sg_poly)
y_sg_full = savgol_filter(y_masked, sg_window, sg_poly)

# plt.figure(figsize=(10, 5))
# plt.title("X Position: Raw vs. Smoothed")

# # Plot raw data
# plt.plot(df["Time_stamp"], df["X_raw"], label="X Raw", color="gray", linewidth=1, alpha=0.5)

# # Plot smoothed data
# plt.plot(df["Time_stamp"], x_sg_full, label="X Smoothed (S-G)", color="C2", linewidth=2)

# plt.xlabel("Time (s)")
# plt.ylabel("X Position (px)")
# plt.legend()
# plt.grid(True)
# plt.tight_layout()
# plt.show()


fig, ax = plt.subplots(figsize=(12, 5))
ax.set_title("X Position: Raw vs. IF-Cleaned vs. S-G Smoothed")

# 1. Raw data
ax.plot(df["Time_stamp"], df["X_raw"], label="X Raw (All)", color="0.6", linewidth=1, alpha=0.4)

# 2. Isolation Forest cleaned (interpolated)
ax.plot(df["Time_stamp"], x_masked, label="X After IF (Interpolated)", color="0.3", linewidth=1, alpha=0.7)

# 3. S-G smoothed after IF
ax.plot(df["Time_stamp"], x_sg_full, label="X S-G Smoothed (Post IF)", color="red", linewidth=2)

# # Chamber arrival lines
# if "Chamber_arrival_Time" in df.columns:
#     arrival_times = df["Chamber_arrival_Time"].dropna()
#     arrival_times = arrival_times[arrival_times > 0].unique()
#     for t in arrival_times:
#         ax.axvline(x=t, color="red", linestyle="--", linewidth=1.5, label="Chamber Arrival")

# # Odor choice lines
# if "Odor_choice_time" in df.columns:
#     choice_times = df["Odor_choice_time"].dropna()
#     choice_times = choice_times[choice_times > 0].unique()
#     for t in choice_times:
#         ax.axvline(x=t, color="green", linestyle=":", linewidth=1.5, label="Odor Choice")

ax.set_xlabel("Time (s)")
ax.set_ylabel("X Position (px)")
ax.legend()
ax.grid(False)
fig.tight_layout()
plt.savefig("filtered_X_data.svg", format="svg")
plt.show()



fig, ax = plt.subplots(figsize=(12, 5))
ax.set_title("Y Position: Raw vs. IF-Cleaned vs. S-G Smoothed")

# 1. Raw data (before any filtering)
ax.plot(df["Time_stamp"], df["Y_raw"], label="y Raw (All)", color="gray", linewidth=1, alpha=0.4)

# 2. Isolation Forest cleaned (interpolated)
ax.plot(df["Time_stamp"], y_masked, label="y After IF (Interpolated)", color="yellow", linewidth=1.5, alpha=0.7)

# 3. S-G smoothed after IF
ax.plot(df["Time_stamp"], y_sg_full, label="y S-G Smoothed (Post IF)", color="red", linewidth=2)

# Chamber arrival vertical lines with label only once
if "Chamber_arrival_Time" in df.columns:
    arrival_times = df["Chamber_arrival_Time"].dropna()
    arrival_times = arrival_times[arrival_times > 0].unique()
    labeled = False
    for t in arrival_times:
        if not labeled:
            ax.axvline(x=t, color="red", linestyle="--", linewidth=1.5, label="Chamber Arrival")
            labeled = True
        else:
            ax.axvline(x=t, color="red", linestyle="--", linewidth=1.5)

# Odor choice vertical lines with label only once
if "Odor_choice_time" in df.columns:
    choice_times = df["Odor_choice_time"].dropna()
    choice_times = choice_times[choice_times > 0].unique()
    labeled = False
    for t in choice_times:
        if not labeled:
            ax.axvline(x=t, color="green", linestyle=":", linewidth=1.5, label="Odor Choice")
            labeled = True
        else:
            ax.axvline(x=t, color="green", linestyle=":", linewidth=1.5)

ax.set_xlabel("Time (s)")
ax.set_ylabel("y Position (px)")
ax.legend()
ax.grid(False)
fig.tight_layout()

plt.show()


#%% displacement 
df["dx"] = x_sg_full
df["dy"] = y_sg_full
df["dt"] = df["Time_stamp"].diff()

df["displacement"] = np.sqrt(df["dx"]**2 + df["dy"]**2)
df["speed"]        = df["displacement"] / df["dt"]
df["acceleration"] = df["speed"].diff() / df["dt"]

fig, ax = plt.subplots(figsize=(10,4))
ax.plot(df["Time_stamp"], df["displacement"], color="C0")

# Chamber arrival vertical lines with label only once
if "Chamber_arrival_Time" in df.columns:
    arrival_times = df["Chamber_arrival_Time"].dropna()
    arrival_times = arrival_times[arrival_times > 0].unique()
    labeled = False
    for t in arrival_times:
        if not labeled:
            ax.axvline(x=t, color="red", linestyle="--", linewidth=1.5, label="Chamber Arrival")
            labeled = True
        else:
            ax.axvline(x=t, color="red", linestyle="--", linewidth=1.5)

# Odor choice vertical lines with label only once
if "Odor_choice_time" in df.columns:
    choice_times = df["Odor_choice_time"].dropna()
    choice_times = choice_times[choice_times > 0].unique()
    labeled = False
    for t in choice_times:
        if not labeled:
            ax.axvline(x=t, color="green", linestyle=":", linewidth=1.5, label="Odor Choice")
            labeled = True
        else:
            ax.axvline(x=t, color="green", linestyle=":", linewidth=1.5)

plt.title("Displacement over Time (Savitzky–Golay Smoothed)")
plt.xlabel("Time (s)")
plt.ylabel("Displacement (pixels)")
plt.tight_layout()

plt.savefig("displacement_plot.svg", format="svg")

plt.show()


#%% speed
fig, ax = plt.subplots(figsize=(10,4))  # Use subplots to get ax
ax.plot(df["Time_stamp"], df["speed"], color="C1")

# Chamber arrival: red dashed verticals
if "Chamber_arrival_Time" in df.columns:
    arrival_times = df["Chamber_arrival_Time"].dropna()
    arrival_times = arrival_times[arrival_times > 0].unique()  # drop any zero entries
    labeled = False
    for t in arrival_times:
        if not labeled:
            ax.axvline(x=t, color="red", linestyle="--", linewidth=1.5, label="Chamber Arrival")
            labeled = True
        else:
            ax.axvline(x=t, color="red", linestyle="--", linewidth=1.5)

# Odor choice: green dotted verticals
if "Odor_choice_time" in df.columns:
    choice_times = df["Odor_choice_time"].dropna()
    choice_times = choice_times[choice_times > 0].unique()  # drop zero
    labeled = False
    for t in choice_times:
        if not labeled:
            ax.axvline(x=t, color="green", linestyle=":", linewidth=1.5, label="Odor Choice")
            labeled = True
        else:
            ax.axvline(x=t, color="green", linestyle=":", linewidth=1.5)

# Unique legend entries
handles, labels = ax.get_legend_handles_labels()
by_label = dict(zip(labels, handles))
ax.legend(by_label.values(), by_label.keys())

ax.set_title("Speed over Time")
ax.set_xlabel("Time (s)")
ax.set_ylabel("Speed (pixels/s)")
plt.tight_layout()


plt.savefig("speed_plot.svg", format="svg")


plt.show()


#%% velocity 

import matplotlib.ticker as ticker

# Compute dt
df["dt"] = df["Time_stamp"].diff()

# Store smoothed positions
df["x_sg"] = x_sg_full
df["y_sg"] = y_sg_full

# Compute derivatives (vx, vy) = position change / time change
df["vx"] = df["x_sg"].diff() / df["dt"]
df["vy"] = df["y_sg"].diff() / df["dt"]

# Optional: Velocity magnitude (should match speed if direction is ignored)
df["velocity_magnitude"] = np.sqrt(df["vx"]**2 + df["vy"]**2)

fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(df["Time_stamp"], df["vx"], label="Vx (X Velocity)", color="0.6",linewidth=0.5)
ax.plot(df["Time_stamp"], df["vy"], label="Vy (Y Velocity)", color="0.3",linewidth=0.5)
ax.plot(df["Time_stamp"], df["velocity_magnitude"], label="Velocity", color="red",linewidth=1)

# Optional event lines
if "Chamber_arrival_Time" in df.columns:
    for t in df["Chamber_arrival_Time"].dropna().unique():
        if t > 0:
            ax.axvline(x=t, color="black", linestyle="--", linewidth=1, label="Chamber Arrival")

if "Odor_choice_time" in df.columns:
    for t in df["Odor_choice_time"].dropna().unique():
        if t > 0:
            ax.axvline(x=t, color="black", linestyle="-", linewidth=1, label="Odor Choice")

# Clean up duplicate legend entries
handles, labels = ax.get_legend_handles_labels()
unique = dict(zip(labels, handles))

ax.xaxis.set_major_locator(ticker.MaxNLocator(nbins=20))  # Increase number of ticks on x-axis
ax.legend(unique.values(), unique.keys())

ax.set_title("Velocity Components and Magnitude over Time")
ax.set_xlabel("Time (s)")
ax.set_ylabel("Velocity (pixels/s)")
plt.tight_layout()


plt.savefig("velocity_plot.svg", format="svg")

plt.show()



#%%

'''
3D plot
'''
# import matplotlib.pyplot as plt
# from mpl_toolkits.mplot3d import Axes3D  # needed to enable 3D plotting, even if unused directly

# fig = plt.figure(figsize=(10, 7))
# ax = fig.add_subplot(111, projection='3d')

# # Scatter plot of X, Y, Time_stamp
# sc = ax.scatter(x_sg_full, y_sg_full, df["Time_stamp"], c=df["Time_stamp"], cmap='viridis', s=20)

# ax.set_xlabel("X Position")
# ax.set_ylabel("Y Position")
# ax.set_zlabel("Time (s)")
# ax.set_title("3D Trajectory: X, Y over Time")

# fig.colorbar(sc, label='Time (s)')

# plt.show()




# #%%  SAVITZKY–GOLAY ON MEDIAN OUTPUT ────────────────────────────────
# # ensure odd & ≤ length
# n = len(df["X_raw"][df["IF_pred"] == 1])
# if sg_window % 2 == 0: sg_window += 1
# if sg_window > n: sg_window = n//2*2 - 1
# if sg_poly >= sg_window: sg_poly = sg_window - 1

# x_sg = savgol_filter(df["X_raw"][df["IF_pred"] == 1], sg_window, sg_poly)
# y_sg = savgol_filter(df["Y_raw"][df["IF_pred"] == 1], sg_window, sg_poly)


# # Plot S-G outputs
# fig, axes = plt.subplots(2, 1, figsize=(10, 6), sharex=True)
# fig.suptitle(f"Savitzky–Golay Smoothed Positions (w={sg_window}, p={sg_poly})", fontsize=14)
# axes[0].plot(x_sg, color="C2", label="X_sg")
# axes[0].set_ylabel("X_sg (px)")
# axes[0].legend(loc="upper right")
# axes[1].plot(y_sg, color="C3", label="Y_sg")
# axes[1].set_ylabel("Y_sg (px)")
# axes[1].set_xlabel("Time (s)")
# axes[1].legend(loc="upper right")
# plt.tight_layout(rect=[0,0,1,0.95])
# plt.show()





    
