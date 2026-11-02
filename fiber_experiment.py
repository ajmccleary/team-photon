#!/usr/bin/env python3
"""Interactive Matplotlib visualization of a fiber optics experiment."""

import math
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.widgets import Button, Slider

# Draw the experiment and calculate optical properties
def draw_experiment(ax, n_core, n_cladding, n_medium, incident_angle):
    ax.clear()

    core_radius = 0.50
    entry_x = 1.25
    fiber_end = 8.75

    # Cladding
    ax.add_patch(Rectangle((entry_x, -0.72), fiber_end - entry_x, 1.44,
                           facecolor="lightblue", edgecolor="slategray", linewidth=1.5))
    # Core
    ax.add_patch(Rectangle((entry_x, -core_radius), fiber_end - entry_x, 2 * core_radius,
                           facecolor="gold", edgecolor="darkgoldenrod", linewidth=1.5))

    ax.axvline(entry_x, color="black", linestyle="--", linewidth=1, alpha=0.7)
    ax.text(entry_x - 0.05, 0.5, "Fiber Optic Entry Face", ha="right", fontsize=10)

    valid = 0 < n_cladding < n_core and n_medium > 0

    if valid:
        # Calculate the critical angle from Snell's law at the core-cladding boundary
        critical_angle = math.degrees(math.asin(n_cladding / n_core))

        # Calculate the numerical aperture and external acceptance angle
        numerical_aperture = math.sqrt(max(0.0, n_core ** 2 - n_cladding ** 2))
        
        # Calculate max acceptance angle properly 
        if numerical_aperture > n_medium:
            acceptance_angle = 90.0
        else:
            acceptance_angle = math.degrees(math.asin(numerical_aperture / n_medium))

        # Refract the ray from the surrounding medium into the fiber core
        sine_internal = n_medium * math.sin(math.radians(incident_angle)) / n_core
        if abs(sine_internal) <= 1:
            internal_angle = math.degrees(math.asin(sine_internal))
        else:
            internal_angle = 90.0
            
        # Check if the ray achieves Total Internal Reflection at the core-cladding boundary
        boundary_angle = 90.0 - internal_angle
        
        # Floating point math tolerance added so boundary threshold cases calculate properly
        epsilon = 1e-9
        guided = (boundary_angle + epsilon >= critical_angle) and abs(sine_internal) <= 1
    else:
        critical_angle = float("nan")
        numerical_aperture = float("nan")
        acceptance_angle = float("nan")
        internal_angle = float("nan")
        guided = False

    # Draw the incoming ray and light source
    source_x = 0.15
    entry_y = 0.0  # force the ray to always hit the exact center of the core
    
    # calculate the source's starting height backwards from the entry point
    source_y = -math.tan(math.radians(incident_angle)) * (entry_x - source_x)
    
    ax.plot([source_x, entry_x], [source_y, entry_y], color="red", linewidth=2.3,
            solid_capstyle="round", label="Incoming Light Ray")
    ax.scatter([source_x], [source_y], color="red", s=55, zorder=5)

    if valid:
        if guided:
            # Trace repeated reflections along the fiber core
            x_values = [entry_x]
            y_values = [entry_y]
            x = entry_x
            y = entry_y
            
            # Since it always enters at y=0, it will always move towards the top boundary first if internal_angle > 0
            moving_up = internal_angle >= 0

            for _ in range(24):
                if abs(internal_angle) < 0.001:
                    x_next = fiber_end
                    y_next = y
                else:
                    boundary = core_radius if moving_up else -core_radius
                    # Use absolute value of tan to ensure distance is always positive
                    horizontal_distance = abs(boundary - y) / math.tan(math.radians(abs(internal_angle)))
                    x_next = min(fiber_end, x + horizontal_distance)
                    
                    if x_next < fiber_end:
                        y_next = boundary
                    else:
                        current_angle = abs(internal_angle) if moving_up else -abs(internal_angle)
                        y_next = y + math.tan(math.radians(current_angle)) * (x_next - x)

                x_values.append(x_next)
                y_values.append(y_next)
                if x_next >= fiber_end:
                    break
                x, y = x_next, y_next
                moving_up = not moving_up

            ax.plot(x_values, y_values, color="green", linewidth=2.3,
                    solid_capstyle="round", label="Guided Light Ray")
            status = "SUCCESS: Guided via Total Internal Reflection"
            status_color = "green"
        else:
            # Draw a ray that exits the fiber because it is outside the acceptance cone
            sine_out = n_core * math.sin(math.radians(boundary_angle)) / n_cladding
            if abs(sine_out) <= 1:
               refracted_boundary_angle = math.degrees(math.asin(sine_out))
               exit_angle_relative_to_axis = 90.0 - refracted_boundary_angle
            else:
               exit_angle_relative_to_axis = internal_angle

            boundary_hit_y = core_radius if internal_angle >= 0 else -core_radius
            horizontal_dist_to_boundary = abs(boundary_hit_y - entry_y) / math.tan(math.radians(internal_angle)) if internal_angle != 0 else 999
            
            x_boundary = entry_x + horizontal_dist_to_boundary
            ax.plot([entry_x, x_boundary], [entry_y, boundary_hit_y], color="red", linewidth=2.3)
            
            x_final = x_boundary + 1.5
            y_final = boundary_hit_y + (math.tan(math.radians(exit_angle_relative_to_axis)) * 1.5 if internal_angle >= 0 else -math.tan(math.radians(exit_angle_relative_to_axis)) * 1.5)
            
            ax.plot([x_boundary, x_final], [boundary_hit_y, y_final], color="red", linewidth=2.3, label="Lost Light Ray")
                    
            status = "FAILED: Lost (Outside Acceptance Cone)"
            status_color = "darkred"
    else:
        status = "ERROR: Core Refractive Index must be > Cladding Index"
        status_color = "darkred"

    ax.set_xlim(0, 9.0)
    ax.set_ylim(-1.50, 1.50)
    ax.set_aspect("equal")
    ax.set_title("Step-Index Optical Fiber Experiment", fontsize=16, pad=16)
    ax.set_xlabel("Fiber Length Position", fontsize=11)
    ax.set_yticks([])

    ax.text(0.02, 0.96, status, transform=ax.transAxes, color=status_color,
            fontsize=12, fontweight="bold", va="top",
            bbox={"boxstyle": "round,pad=0.6", "facecolor": "white", "alpha": 0.95, "edgecolor": status_color})

    ax.text(0.02, 0.81,
            f"Core Refractive Index: {n_core:.3f}\nCladding Refractive Index: {n_cladding:.3f}\nExternal Medium Index: {n_medium:.3f}",
            transform=ax.transAxes, fontsize=10, va="top", linespacing=1.8,
            bbox={"boxstyle": "round,pad=0.6", "facecolor": "whitesmoke", "alpha": 0.95, "edgecolor": "lightgray"})

    if valid:
        ax.text(0.98, 0.96,
                f"Incident Angle: {incident_angle:.2f}°\n"
                f"Internal Refracted Angle: {internal_angle:.2f}°\n"
                f"Core-Cladding Critical Angle: {critical_angle:.2f}°\n"
                f"Max Acceptance Angle: {acceptance_angle:.2f}°\n"
                f"Numerical Aperture: {numerical_aperture:.4f}",
                transform=ax.transAxes, ha="right", va="top", fontsize=10, linespacing=1.8,
                bbox={"boxstyle": "round,pad=0.6", "facecolor": "whitesmoke", "alpha": 0.95, "edgecolor": "lightgray"})

def main():
    # Create figure
    fig = plt.figure(figsize=(30, 20))
    fig.canvas.manager.set_window_title("Interactive Fiber Optics Experiment")

    # Create elements of the figure
    experiment_ax = fig.add_axes([0.05, 0.38, 0.90, 0.55])  
    core_ax = fig.add_axes([0.10, 0.25, 0.40, 0.03])
    cladding_ax = fig.add_axes([0.10, 0.18, 0.40, 0.03])
    medium_ax = fig.add_axes([0.10, 0.11, 0.40, 0.03])
    angle_ax = fig.add_axes([0.10, 0.04, 0.40, 0.03])

    # Create sliders
    core_slider = Slider(core_ax, "Core Index", 1.30, 1.70, valinit=1.48, valstep=0.01, color="blue")
    cladding_slider = Slider(cladding_ax, "Cladding Index", 1.30, 1.70, valinit=1.46, valstep=0.01, color="gray")
    medium_slider = Slider(medium_ax, "Medium Index", 1.00, 1.60, valinit=1.00, valstep=0.01, color="purple")
    angle_slider = Slider(angle_ax, "Incident Angle (degrees)", 0.0, 45.0, valinit=14.0, valstep=0.5, color="red")

    # Handle updating graphics
    def update(_value):
        draw_experiment(experiment_ax, core_slider.val, cladding_slider.val, medium_slider.val, angle_slider.val)
        fig.canvas.draw_idle()

    core_slider.on_changed(update)
    cladding_slider.on_changed(update)
    medium_slider.on_changed(update)
    angle_slider.on_changed(update)

    # Create buttons
    standard_ax = fig.add_axes([0.62, 0.18, 0.14, 0.04])
    dense_ax = fig.add_axes([0.79, 0.18, 0.16, 0.04])

    standard_button = Button(standard_ax, "Standard Fiber Preset")
    dense_button = Button(dense_ax, "High Index Difference Preset")

    def set_standard(_event=None):
        core_slider.set_val(1.48)
        cladding_slider.set_val(1.46)
        medium_slider.set_val(1.00)
        angle_slider.set_val(14.0)

    def set_dense(_event=None):
        core_slider.set_val(1.65)
        cladding_slider.set_val(1.35)
        medium_slider.set_val(1.00)
        angle_slider.set_val(35.0)

    standard_button.on_clicked(set_standard)
    dense_button.on_clicked(set_dense)

    # Display experiment
    draw_experiment(experiment_ax, 1.48, 1.46, 1.00, 14.0)
    plt.show()

if __name__ == "__main__":
    main()