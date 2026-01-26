"""
Paquete de servicios biométricos.
Expone las funciones principales de manera limpia.
"""

from .encoders import (
    decode_base64_image,
    detect_faces,
    extract_face_encodings,
    prepare_image_for_encoding,
)

from .pose_checks import (
    validate_pose,
    analyze_face_structure,
    get_face_metrics,
    eye_aspect_ratio,
)

from .repository import (
    save_face_encoding,
    load_face_encoding,
    get_all_face_encodings,
    compare_faces,
    find_matching_user,
    clear_face_encoding,
)

from .pipelines import (
    enroll_biometric_pipeline,
    login_biometric_pipeline,
    validate_pose_challenge,
)

__all__ = [
    # Encoders
    'decode_base64_image',
    'detect_faces',
    'extract_face_encodings',
    'prepare_image_for_encoding',
    # Pose checks
    'validate_pose',
    'analyze_face_structure',
    'get_face_metrics',
    'eye_aspect_ratio',
    # Repository
    'save_face_encoding',
    'load_face_encoding',
    'get_all_face_encodings',
    'compare_faces',
    'find_matching_user',
    'clear_face_encoding',
    # Pipelines
    'enroll_biometric_pipeline',
    'login_biometric_pipeline',
    'validate_pose_challenge',
]
