def safe_element_get(_list: [], index: int, default=None) -> int:
    """
    Get an element from a list checking if both the list and the element exist

    :param default: Default value to return if list or element are non existent
    :param _list: List to extract the element from
    :param index: Index of the element in the list
    :return: The expected element if exists, None if it doesn't
    """

    return _list[index] if _list is not None and len(_list) > index else default
