# utils/three_d.py
import numpy as np
import plotly.graph_objects as go
import math

# 3 fixed level nodes (you can change coordinates if you expand levels)
NODES = {"L1": (0, 0, 0.25), "L2": (2.0, 1.0, 0.65), "L3": (4.0, 0.0, 1.05)}

def _island_surface(n=90):
    xs = np.linspace(-3, 7, n)
    ys = np.linspace(-3, 3, n)
    X, Y = np.meshgrid(xs, ys)
    # Island shape: gaussian hill + gentle ridges
    cx, cy = 2.0, 0.0
    Z = 1.25 * np.exp(-((X - cx) ** 2 + (Y - cy) ** 2) / 6.0) + 0.15 * np.sin(1.3 * X) * np.cos(1.0 * Y)
    water = -0.10
    Z = np.maximum(Z, water)
    return X, Y, Z, water

def render_map(current_level="L1"):
    """Backward compatible simple map."""
    return render_map_animated(current_level=current_level, solved=set(), reduced_motion=True)

def render_map_animated(current_level="L1", solved=set(), reduced_motion=False):
    X, Y, Z, water = _island_surface()
    fig = go.Figure()

    # Island surface
    fig.add_trace(go.Surface(x=X, y=Y, z=Z, showscale=False, opacity=0.96))
    # Water plane (downsampled grid to keep it light)
    fig.add_trace(go.Surface(
        x=X[::6, ::6], y=Y[::6, ::6], z=np.full_like(X[::6, ::6], water),
        colorscale=[[0, '#7ec8e3'], [1, '#7ec8e3']], showscale=False, opacity=0.6
    ))

    # Level path
    xs = [NODES["L1"][0], NODES["L2"][0], NODES["L3"][0]]
    ys = [NODES["L1"][1], NODES["L2"][1], NODES["L3"][1]]
    zs = [NODES["L1"][2], NODES["L2"][2], NODES["L3"][2]]
    fig.add_trace(go.Scatter3d(x=xs, y=ys, z=zs, mode="lines", line=dict(width=6)))

    labels = ["L1", "L2", "L3"]
    colors, sizes = [], []
    for lab in labels:
        if lab in solved:
            colors.append("#22c55e")     # solved -> green
            sizes.append(12)
        elif lab == current_level:
            colors.append("#f59e0b")     # current -> amber
            sizes.append(14)
        else:
            colors.append("#9ca3af")     # locked -> gray
            sizes.append(10)

    fig.add_trace(go.Scatter3d(
        x=xs, y=ys, z=zs, mode="markers+text", text=labels, textposition="top center",
        marker=dict(size=sizes, color=colors), name="levels"
    ))

    # Animation: pulse the current marker + reveal path up to current/solved
    if not reduced_motion:
        frames = []
        # How many segments of the path to show (L1->L2->L3)
        seg = min(2, len([1 for lab in labels if (lab in solved) or (lab == current_level)]))
        for k in range(24):
            # Pulsing sizes
            pulse_sizes = []
            for lab in labels:
                base = 14 if lab == current_level else 12 if lab in solved else 10
                amp = 4 if lab == current_level else 0
                size = base + int(amp * (0.5 + 0.5 * math.sin(2 * math.pi * (k / 24))))
                pulse_sizes.append(size)

            # Path reveal
            xline = xs[:seg + 1]
            yline = ys[:seg + 1]
            zline = zs[:seg + 1]

            frames.append(go.Frame(
                data=[
                    fig.data[0],  # island
                    fig.data[1],  # water
                    go.Scatter3d(x=xline, y=yline, z=zline, mode="lines", line=dict(width=6)),
                    go.Scatter3d(
                        x=xs, y=ys, z=zs, mode="markers+text", text=labels, textposition="top center",
                        marker=dict(size=pulse_sizes, color=colors)
                    ),
                ],
                name=f"f{k}"
            ))
        fig.frames = frames
        fig.update_layout(
            updatemenus=[{
                "type": "buttons",
                "showactive": False,
                "buttons": [
                    {"label": "▶ Play", "method": "animate",
                     "args": [None, {"frame": {"duration": 80, "redraw": True}, "fromcurrent": True,
                                     "transition": {"duration": 0}}]},
                    {"label": "⏸ Pause", "method": "animate",
                     "args": [[None], {"mode": "immediate", "frame": {"duration": 0, "redraw": False},
                                       "transition": {"duration": 0}}]}
                ],
                "x": 0.02, "y": 0.02
            }]
        )

    fig.update_layout(
        height=520, margin=dict(l=0, r=0, t=0, b=0),
        scene=dict(
            xaxis=dict(visible=False), yaxis=dict(visible=False), zaxis=dict(visible=False),
            aspectmode="data",
            camera=dict(eye=dict(x=1.6, y=1.6, z=0.9))
        )
    )
    return fig
