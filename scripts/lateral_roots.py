import numpy as np
from scipy import ndimage
from skimage.morphology import skeletonize

from config import SCALE_PX_PER_CM, lr_min_branch_len_px, lr_min_separation_px
from utils import _find_nearest_path_index

_SQRT2 = np.sqrt(2)
_NEIGHBOR_OFFSETS = [(-1, -1), (-1, 0), (-1, 1), (0, -1),
                     (0, 1), (1, -1), (1, 0), (1, 1)]


def _neighbor_counts(skeleton):
    """Count 8-connected skeleton neighbors for each skeleton pixel."""
    kernel = np.ones((3, 3), dtype=np.uint8)
    counts = ndimage.convolve(skeleton.astype(np.uint8), kernel,
                              mode='constant', cval=0)
    return counts - skeleton.astype(np.uint8)


def _local_tangent(path, idx, window=5):
    """Tangent direction of path at idx, from neighbouring path points."""
    n = len(path)
    i0 = max(0, idx - window)
    i1 = min(n - 1, idx + window)
    if i0 == i1:
        return np.array([1.0, 0.0])
    vec = path[i1].astype(float) - path[i0].astype(float)
    norm = np.linalg.norm(vec)
    if norm == 0:
        return np.array([1.0, 0.0])
    return vec / norm


def classify_side(path, point):
    """Classify a point as 'left' or 'right' of the path's local direction.

    path : Nx2 array of (row, col), ordered top to tip.
    point : (row, col)
    """
    path = np.asarray(path)
    idx = _find_nearest_path_index(path, point)
    tangent = _local_tangent(path, idx)
    to_point = np.asarray(point, dtype=float) - path[idx].astype(float)
    cross = tangent[0] * to_point[1] - tangent[1] * to_point[0]
    return 'left' if cross < 0 else 'right'


def _walk_branch(skeleton, path_mask, start, max_steps=2000):
    """Walk skeleton pixels off the primary path from `start`, 8-connected.

    Returns (length_px, tip) — total step length and the furthest pixel
    reached (used as the point to classify left/right).
    """
    h, w = skeleton.shape
    visited = {start}
    frontier = [start]
    length = 0.0
    tip = start
    steps = 0
    while frontier and steps < max_steps:
        steps += 1
        r, c = frontier.pop()
        for dr, dc in _NEIGHBOR_OFFSETS:
            nr, nc = r + dr, c + dc
            if not (0 <= nr < h and 0 <= nc < w):
                continue
            if (nr, nc) in visited:
                continue
            if not skeleton[nr, nc] or path_mask[nr, nc]:
                continue
            visited.add((nr, nc))
            step_len = _SQRT2 if (dr != 0 and dc != 0) else 1.0
            length += step_len
            frontier.append((nr, nc))
            tip = (nr, nc)
    return length, tip


def detect_lateral_roots(binary, path, scale=SCALE_PX_PER_CM):
    """Detect lateral root branch points off a traced primary root.

    Args:
        binary: 2-D bool array, the plate's binary root mask (same mask
            used to trace the primary root).
        path: Nx2 array of (row, col) skeleton pixels for the primary
            root, ordered top to tip (as returned by trace_root).
        scale: pixels per cm.

    Returns:
        list of {'row', 'col', 'side'} dicts, ordered top to tip.
    """
    path = np.asarray(path)
    if path.size == 0:
        return []

    skeleton = skeletonize(binary)
    h, w = skeleton.shape

    in_bounds = ((path[:, 0] >= 0) & (path[:, 0] < h) &
                 (path[:, 1] >= 0) & (path[:, 1] < w))
    path = path[in_bounds]
    if len(path) == 0:
        return []

    path_mask = np.zeros(skeleton.shape, dtype=bool)
    path_mask[path[:, 0], path[:, 1]] = True

    neighbor_counts = _neighbor_counts(skeleton)
    min_branch_len = lr_min_branch_len_px(scale)
    min_separation = lr_min_separation_px(scale)

    detections = []  # (path_idx, row, col, side)
    last_idx_by_side = {}

    for idx, (r, c) in enumerate(path):
        if not skeleton[r, c] or neighbor_counts[r, c] < 3:
            continue
        for dr, dc in _NEIGHBOR_OFFSETS:
            nr, nc = r + dr, c + dc
            if not (0 <= nr < h and 0 <= nc < w):
                continue
            if not skeleton[nr, nc] or path_mask[nr, nc]:
                continue
            branch_len, tip = _walk_branch(skeleton, path_mask, (nr, nc))
            if branch_len < min_branch_len:
                continue
            side = classify_side(path, tip)
            last_idx = last_idx_by_side.get(side)
            if last_idx is not None and (idx - last_idx) < min_separation:
                continue
            last_idx_by_side[side] = idx
            detections.append((idx, r, c, side))

    return [{'row': int(r), 'col': int(c), 'side': side}
            for idx, r, c, side in detections]
