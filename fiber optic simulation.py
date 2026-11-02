#!/usr/bin/env python3
"""Interactive Matplotlib visualization of a step-index fiber optics experiment."""

import math
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.widgets import Button, Slider


# Draw the experiment and calculate the optical properties
def draw_experiment(ax, n_core, n_cladding, n_medium, incident_angle):
    ax.clear()

    core_radius = 0.50
    entry_x = 1.25
    fiber_end = 8.75

    ax.add_patch(Rectangle((entry_x, -0.72), fiber_end - entry_x, 1.44,
                           facecolor="#b8d4e3", edgecolor="#738ba0", linewidth=1.5))
    ax.add_patch(Rectangle((entry_x, -core_radius), fiber_end - entry_x, 2 * core_radius,
                           facecolor="#ffd166", edgecolor="#c99300", linewidth=1.5))

    ax.axvline(entry_x, color="#333333", linestyle="--", linewidth=1, alpha=0.7)
    ax.text(entry_x - 0.05, 0.82, "fiber entry face", ha="right", fontsize=9)

    valid = 0 < n_cladding < n_core and n_medium > 0

    if valid:
        # Calculate the critical angle from Snell's law at the core-cladding boundary
        critical_angle = math.degrees(math.asin(n_cladding / n_core))

        # Calculate the numerical aperture and external acceptance angle
        numerical_aperture = math.sqrt(max(0.0, n_core ** 2 - n_cladding ** 2))
        acceptance_angle = math.degrees(math.asin(min(1.0, numerical_aperture / n_medium)))

        # Refract the ray from the surrounding medium into the fiber core
        sine_internal = n_medium * math.sin(math.radians(incident_angle)) / n_core
        if abs(sine_internal) <= 1:
            internal_angle = math.degrees(math.asin(sine_internal))
        else:
            internal_angle = 90.0

        guided = 0 <= incident_angle <= acceptance_angle
    else:
        critical_angle = float("nan")
        numerical_aperture = float("nan")
        acceptance_angle = float("nan")
        internal_angle = float("nan")
        guided = False

    # Draw the incoming ray and light source
    source_x = 0.15
    entry_y = math.tan(math.radians(incident_angle)) * (entry_x - source_x)
    ax.plot([source_x, entry_x], [0, entry_y], color="#e63946", linewidth=2.3,
            solid_capstyle="round", label="incoming ray")
    ax.scatter([source_x], [0], color="#e63946", s=55, zorder=5)

    if valid:
        if guided:
            # Trace repeated reflections along the fiber core
            x_values = [entry_x]
            y_values = [entry_y]
            x = entry_x
            y = entry_y
            moving_up = internal_angle >= 0

            for _ in range(24):
                if abs(internal_angle) < 0.001:
                    x_next = fiber_end
                    y_next = y
                else:
                    boundary = core_radius if moving_up else -core_radius
                    horizontal_distance = abs(boundary - y) / math.tan(math.radians(internal_angle))
                    x_next = min(fiber_end, x + horizontal_distance)
                    y_next = boundary if x_next < fiber_end else y + math.tan(math.radians(internal_angle)) * (x_next - x)

                x_values.append(x_next)
                y_values.append(y_next)
                if x_next >= fiber_end:
                    break
                x, y = x_next, y_next
                moving_up = not moving_up

            ax.plot(x_values, y_values, color="#159947", linewidth=2.3,
                    solid_capstyle="round", label="guided ray")
            status = "GUIDED â€” total internal reflection"
            status_color = "#159947"
        else:
            # Draw a ray that exits the fiber because it is outside the acceptance cone
            x_next = entry_x + 2.2
            y_next = entry_y + math.tan(math.radians(internal_angle)) * 2.2
            ax.plot([entry_x, x_next], [entry_y, y_next], color="#e63946",
                    linewidth=2.3, label="ray lost")
            status = "LOST â€” outside acceptance cone"
            status_color = "#b42318"
    else:
        status = "INVALID â€” core index must exceed cladding index"
        status_color = "#b42318"

    ax.set_xlim(0, 9.0)
    ax.set_ylim(-1.15, 1.15)
    ax.set_aspect("equal")
    ax.set_title("Step-Index Optical Fiber Experiment", fontsize=14, pad=12)
    ax.set_xlabel("position along the fiber")
    ax.set_yticks([])

    ax.text(0.02, 0.96, status, transform=ax.transAxes, color=status_color,
            fontsize=11, fontweight="bold", va="top",
            bbox=dict(boxstyle="round,pad=0.35", facecolor="white", alpha=0.95,
                      edgecolor=status_color))

    ax.text(0.02, 0.74,
            f"Core index: {n_core:.3f}\nCladding index: {n_cladding:.3f}\nMedium index: {n_medium:.3f}",
            transform=ax.transAxes, fontsize=9, va="top",
            bbox=dict(boxstyle="round,pad=0.35", facecolor="#f7f9fb", alpha=0.95,
                      edgecolor="#ccd6dd"))

    if valid:
        ax.text(0.98, 0.96,
                f"Incident angle: {incident_angle:.2f}Â°\n"
                f"Internal angle: {internal_angle:.2f}Â°\n"
                f"Critical angle: {critical_angle:.2f}Â°\n"
                f"Acceptance angle: {acceptance_angle:.2f}Â°\n"
                f"Numerical aperture: {numerical_aperture:.4f}",
                transform=ax.transAxes, ha="right", va="top", fontsize=9,
                bbox=dict(boxstyle="round,pad=0.35", facecolor="#f7f9fb", alpha=0.95,
                          edgecolor="#ccd6dd"))


# Create the interactive Matplotlib window
def main():
    plt.close("all")
    fig = plt.figure(figsize=(12, 8))
    fig.canvas.manager.set_window_title("Interactive Fiber Optics Experiment")

    experiment_ax = fig.add_axes([0.08, 0.34, 0.84, 0.58])

    core_ax = fig.add_axes([0.09, 0.255, 0.38, 0.035])
    cladding_ax = fig.add_axes([0.09, 0.195, 0.38, 0.035])
    medium_ax = fig.add_axes([0.09, 0.135, 0.38, 0.035])
    angle_ax = fig.add_axes([0.09, 0.075, 0.38, 0.035])

    core_slider = Slider(core_ax, "Core index", 1.30, 1.70, valinit=1.48,
                         valstep=0.01, color="#3a86ff")
    cladding_slider = Slider(cladding_ax, "Cladding index", 1.30, 1.70,
                             valinit=1.46, valstep=0.01, color="#738ba0")
    medium_slider = Slider(medium_ax, "Medium index", 1.00, 1.60,
                           valinit=1.00, valstep=0.01, color="#8338ec")
    angle_slider = Slider(angle_ax, "Incident angle (degrees)", 0.0, 45.0,
                          valinit=14.0, valstep=0.5, color="#e63946")

    # Redraw the complete experiment when any slider changes
    def update(_value):
        draw_experiment(experiment_ax, core_slider.val, cladding_slider.val,
                        medium_slider.val, angle_slider.val)
        fig.canvas.draw_idle()

    core_slider.on_changed(update)
    cladding_slider.on_changed(update)
    medium_slider.on_changed(update)
    angle_slider.on_changed(update)

    standard_ax = fig.add_axes([0.62, 0.205, 0.13, 0.050])
    dense_ax = fig.add_axes([0.76, 0.205, 0.13, 0.050])
    reset_ax = fig.add_axes([0.62, 0.125, 0.27, 0.050])

    standard_button = Button(standard_ax, "Standard fiber")
    dense_button = Button(dense_ax, "Large index difference")
    reset_button = Button(reset_ax, "Reset experiment")

    # Load the standard fiber preset
    def set_standard(_event=None):
        core_slider.set_val(1.48)
        cladding_slider.set_val(1.46)
        medium_slider.set_val(1.00)
        angle_slider.set_val(14.0)

    # Load a high-index-difference fiber preset
    def set_dense(_event=None):
        core_slider.set_val(1.50)
        cladding_slider.set_val(1.40)
        medium_slider.set_val(1.00)
        angle_slider.set_val(14.0)

    standard_button.on_clicked(set_standard)
    dense_button.on_clicked(set_dense)
    reset_button.on_clicked(set_standard)

    draw_experiment(experiment_ax, 1.48, 1.46, 1.00, 14.0)
    plt.show()


if __name__ == "__main__":
    main()
