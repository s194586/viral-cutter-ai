from __future__ import annotations

from .base import LayoutProfile


def build_gameplay_layout() -> LayoutProfile:
    return LayoutProfile(
        content_type="gameplay",
        layout_mode="gameplay_priority_crop",
        layout_policy="gameplay_safe_vertical",
        crop_priority="gameplay",
        allow_face_tracking=True,
        face_tracking_weight=0.2,
        preserve_full_frame=False,
        blur_background=False,
        safe_center_crop=True,
        max_crop_motion=0.08,
        smoothing_strength=0.85,
        min_face_area_for_tracking=0.06,
        ignore_edge_faces=True,
    )
