from .structure import INPUT_FILES, Port


def input_structure() -> tuple[list[list], list[str], list[str]]:
    """
    Create table for structure
    """
    table: list[list] = []
    col_headers: list[str] = []
    row_headers: list[str] = []

    for row in INPUT_FILES.values():
        level, category, domain, port = row

        try:
            row_index = row_headers.index(category)
        except ValueError:
            row_index = len(row_headers)
            row_headers.append(category)

        try:
            col_index = col_headers.index(level)
        except ValueError:
            col_index = len(col_headers)
            col_headers.append(level)

        try:
            row = table[row_index]
        except IndexError:
            row = [[] for i in range(len(col_headers))]
            table.append(row)

        try:
            col = row[col_index]
        except IndexError:
            col = []
            row.append(col)

        if port == Port.EMPTY:
            label = domain
        else:
            label = f"{domain}:{port}"

        col.append(
            {
                "label": label,
                "level": level,
                "category": category,
                "domain": domain,
                "port": port,
                "table": f"{level}_{category}_{domain}_{port}",
            }
        )

    return table, col_headers, row_headers
