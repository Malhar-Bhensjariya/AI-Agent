ALLOWED = {'csv', 'xls', 'xlsx', 'txt', 'json'}


def is_allowed(filename: str) -> bool:
    if not filename or '.' not in filename:
        return False
    return filename.rsplit('.', 1)[1].lower() in ALLOWED
