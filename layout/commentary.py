from __future__ import annotations

from .base import LayoutProfile


def build_commentary_layout() -> LayoutProfile:
    return LayoutProfile(
        content_type="commentary",
        layout_mode="stable_subject_crop",
        layout_policy="stable_subject_or_center",
        crop_priority="subject",
        allow_face_tracking=True,
        face_tracking_weight=0.45,
        preserve_full_frame=False,
        blur_background=False,
        safe_center_crop=True,
        max_crop_motion=0.1,
        smoothing_strength=0.82,
        min_face_area_for_tracking=0.025,
        ignore_edge_faces=False,
    )
