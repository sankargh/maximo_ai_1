from difflib import SequenceMatcher
import re


def match_fields(source_list: list, target_list: list) -> list:
    """
    Compare target_list against source_list and return the best-matching
    source field name for each target field.

    Args:
        source_list: canonical field names  e.g. ["locnum", "id", "description"]
        target_list: fields to remap        e.g. ["locnumber", "desc"]

    Returns:
        list of best-matching source field names in the same order as target_list
    """
    def score(a, b):
        a_norm = re.sub(r"[_\-\s]", "", a).lower()
        b_norm = re.sub(r"[_\-\s]", "", b).lower()
        if a_norm == b_norm:
            return 1.0
        if a_norm in b_norm or b_norm in a_norm:
            return 0.85
        tokens_a = re.split(r"[_\-\s]+", a.lower())
        tokens_b = re.split(r"[_\-\s]+", b.lower())
        token_score = max(
            SequenceMatcher(None, ta, tb).ratio()
            for ta in tokens_a for tb in tokens_b
        )
        char_score = SequenceMatcher(None, a_norm, b_norm).ratio()
        return max(token_score, char_score)

    return [max(source_list, key=lambda s: score(target, s)) for target in target_list]

SQL_KEYWORDS = {
    "select", "from", "where", "and", "or", "not", "in", "is", "null",
    "like", "between", "as", "on", "join", "left", "right", "inner",
    "outer", "group", "by", "order", "having", "distinct", "top", "limit"
}

def fix_clause(clause: str, source_list: list) -> str:
    """
    Fix column names in a SQL clause string by matching against source_list.
    Quoted string values (e.g. 'ACTIVE') are preserved as-is.
    """
    # Extract column tokens, skipping quoted string values
    tokens = re.findall(r"\b[a-zA-Z_][a-zA-Z0-9_]*\b(?=(?:[^']*'[^']*')*[^']*$)", clause)
    columns = [t for t in tokens if t.lower() not in SQL_KEYWORDS]

    if not columns:
        return clause

    matched = match_fields(source_list, columns)
    mapping = dict(zip(columns, matched))

    # Only replace tokens that are outside quoted strings
    def replace_outside_quotes(text, original, fixed):
        parts = re.split(r"('(?:[^']|'')*')", text)  # split on quoted segments
        return "".join(
            re.sub(rf'\b{re.escape(original)}\b', fixed, part)
            if not part.startswith("'") else part
            for part in parts
        )

    for original, fixed in mapping.items():
        clause = replace_outside_quotes(clause, original, fixed)

    return clause

# --- example ---
if __name__ == "__main__":
    source ={
        "Assetnum",
        "Description",
        "AssetType",
        "Status",
        "Location",
        "SiteID",
        "ChangeDate",
    }   
    # target = ["locnumber", "desc", "status", "loc_type", "site_id"]
    select_clause = "change_date, asset_type, description"
    target = [col.strip() for col in select_clause.split(",")]
    result = match_fields(source, target)
    print(result)
    # ['locnum', 'description', 'status', 'type', 'siteid']

    select_clause = "asset_number, description, status"
    where_clause  = "description LIKE 'Machinery%'"

    fixed_select = fix_clause(select_clause, source)
    fixed_where  = fix_clause(where_clause, source)

    print("SELECT", fixed_select)
    print("WHERE ", fixed_where)

