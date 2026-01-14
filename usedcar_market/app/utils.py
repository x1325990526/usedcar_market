import os
import uuid
from werkzeug.utils import secure_filename

def allowed_file(filename: str, allowed_ext: set[str]) -> bool:
    if not filename or "." not in filename:
        return False
    ext = filename.rsplit(".", 1)[1].lower()
    return ext in allowed_ext

def save_upload(file_storage, upload_folder: str, allowed_ext: set[str]) -> str | None:
    if not file_storage or not file_storage.filename:
        return None
    if not allowed_file(file_storage.filename, allowed_ext):
        return None

    safe = secure_filename(file_storage.filename)
    ext = safe.rsplit(".", 1)[1].lower()
    new_name = f"{uuid.uuid4().hex}.{ext}"
    path = os.path.join(upload_folder, new_name)
    file_storage.save(path)
    return new_name
