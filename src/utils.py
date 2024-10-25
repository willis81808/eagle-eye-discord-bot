from typing import List, Dict


def sum_dicts(dict_set: List[Dict[str, float]]) -> Dict[str, float]:
    """
    Sums a set of dictionaries with string keys and numeric values.

    Args:
        dict_set: A set of dictionaries where each dictionary has string keys
            and numeric values

    Returns:
        A new dictionary with the sum of values for each key across all input dictionaries

    Example:
        >>> d1 = {"a": 1, "b": 2}
        >>> d2 = {"b": 3, "c": 4}
        >>> sum_dict_set({d1, d2})
        {'a': 1, 'b': 5, 'c': 4}
    """
    result: Dict[str, float] = {}

    for d in dict_set:
        for key, value in d.items():
            result[key] = result.get(key, 0) + value

    return result
