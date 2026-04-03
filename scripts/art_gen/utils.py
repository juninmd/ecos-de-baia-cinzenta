def parse_chapter_selection(raw: str):
    """
    Parses a string representing a selection of chapters into a sorted, unique list of integers.
    Supports single numbers, comma-separated lists (e.g., '1,2,3'), and ranges (e.g., '10-14').
    """
    selected = []
    # Remove spaces just in case
    clean_args = raw.replace(' ', '')

    if ',' in clean_args:
        parts = clean_args.split(',')
        for part in parts:
            if '-' in part:
                start, end = map(int, part.split('-'))
                selected.extend(range(start, end + 1))
            elif part:
                selected.append(int(part))
    elif '-' in clean_args:
        start, end = map(int, clean_args.split('-'))
        selected.extend(range(start, end + 1))
    elif clean_args:
        selected.append(int(clean_args))

    return sorted(list(set(selected)))
