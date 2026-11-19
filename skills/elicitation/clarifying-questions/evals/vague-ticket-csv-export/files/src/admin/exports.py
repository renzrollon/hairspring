"""CSV helpers shared by the admin console exports (finance extracts today)."""
import csv
import io

EXPORT_ENCODING = "utf-8-sig"  # Excel opens UTF-8 with BOM correctly
EXPORT_DELIMITER = ","


def to_csv(rows, columns):
    """Return CSV text for rows (dicts) in the given column order."""
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=columns, delimiter=EXPORT_DELIMITER)
    writer.writeheader()
    for row in rows:
        writer.writerow({c: row.get(c, "") for c in columns})
    return buf.getvalue().encode(EXPORT_ENCODING)
