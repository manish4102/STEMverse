
def lookup_response(query: str):
    q = query.lower()
    mapping = {
        "newton 3": ("Newton's Third Law: For every action, there is an equal and opposite reaction.", "https://www.youtube.com/watch?v=arwP7fK2F6g"),
        "torque": ("Torque is a twisting force τ = r × F that causes rotation.", "https://www.youtube.com/watch?v=0PDwZC40f5I"),
        "gear ratio": ("Gear ratio compares teeth or radii; larger ratio increases torque but reduces speed.", "https://www.youtube.com/watch?v=p5g6zJYy1n8")
    }
    for k,(ans,vid) in mapping.items():
        if k in q:
            return ans, vid
    return ("I’m not sure yet. Try keywords like 'newton 3', 'torque', or 'gear ratio'.", None)
