from ..utils.chroma_memory import clear_user_memory, export_user_memory, prune_user_memory
from ..utils.logger import log


def clear_memory(user_id: str = None):
    try:
        ok = clear_user_memory(user_id or 'global')
        return {'success': ok}
    except Exception as e:
        log(f"clear_memory error: {str(e)}", 'ERROR')
        return {'error': str(e)}


def export_memory(user_id: str = None):
    try:
        data = export_user_memory(user_id or 'global')
        return {'success': True, 'data': data}
    except Exception as e:
        log(f"export_memory error: {str(e)}", 'ERROR')
        return {'error': str(e)}


def prune_memory(user_id: str = None, keep_last_n: int = 100):
    try:
        ok = prune_user_memory(user_id or 'global', keep_last_n=keep_last_n)
        return {'success': ok}
    except Exception as e:
        log(f"prune_memory error: {str(e)}", 'ERROR')
        return {'error': str(e)}
