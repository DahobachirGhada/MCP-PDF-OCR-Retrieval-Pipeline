def has_tables(page) -> bool:
    """Cheap check with PyMuPDF so Camelot only runs on pages that need it."""
    try:
        return len(page.find_tables().tables) > 0
    except Exception:
        return False