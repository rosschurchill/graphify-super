# DELETED — this shim module is scheduled for removal.
# No callers remain (grepped 2026-05-19); it is kept as a zero-content file
# only because the Write tool cannot delete files.  Remove this file manually:
#   git rm graphify/manifest.py
#
# All three symbols live in graphify.detect:
#   from graphify.detect import save_manifest, load_manifest, detect_incremental
from graphify.detect import save_manifest, load_manifest, detect_incremental

__all__ = ["save_manifest", "load_manifest", "detect_incremental"]
