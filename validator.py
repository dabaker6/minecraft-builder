# Build zone. Every block is checked against this BEFORE being queued, so no
# generated command (or later, no API caller) can place outside the sandbox.
BOUNDS = dict(xmin=0, xmax=128, ymin=0, ymax=64, zmin=0, zmax=128)

def in_bounds(x,y,z) -> bool:
    return (BOUNDS['xmin'] <= x <= BOUNDS['xmax']
            and BOUNDS['ymin'] <= y <= BOUNDS['ymax']
            and BOUNDS['zmin'] <= z <= BOUNDS['zmax']
            )