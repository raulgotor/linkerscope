from logger import logger


class DefaultAppValues:
    DOCUMENT_SIZE = (400, 700)
    POSITION_X = 50
    POSITION_Y = 50
    SIZE_X = 200
    SIZE_Y = 500
    TITLE = ''

def safe_element_list_get(_list: [], index: int, default=None) -> int:
    """
    Get an element from a list checking if both the list and the element exist

    :param default: Default value to return if list or element are non existent
    :param _list: List to extract the element from
    :param index: Index of the element in the list
    :return: The expected element if exists, None if it doesn't
    """

    return _list[index] if _list is not None and len(_list) > index else default


def safe_element_dict_get(_dict: {}, key: str, default=None) -> int:
    """
    Get an element from a dict checking if both the dict and the element exist

    :param default: Default value to return if list or element are non existent
    :param _dict: Dict to extract the element from
    :param key: Key of the key - value pair to extract
    :return: The expected element if exists, None if it doesn't
    """

    return _dict[key] if _dict is not None and key in _dict else default