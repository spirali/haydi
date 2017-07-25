import haydi as hd


def test_limit_string_length():

    string = "1234567890abcdfghijklmnopqrst"
    result = hd.base.utils.limit_string_length(string, 10)
    assert result == "123 ... st"

    result = hd.base.utils.limit_string_length(string, 10000)
    assert result == string

    string = "1234567890"
    result = hd.base.utils.limit_string_length(string, 10)
    assert result == "1234567890"

    string = "12345678901"
    result = hd.base.utils.limit_string_length(string, 10)
    assert result == "123 ... 01"

    string = "12345678901"
    result = hd.base.utils.limit_string_length(string, 11)
    assert result == "12345678901"

    string = "123456789012"
    result = hd.base.utils.limit_string_length(string, 11)
    assert result == "123 ... 012"
