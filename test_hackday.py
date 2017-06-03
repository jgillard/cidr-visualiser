import hackday


# @@@@@@@@@ HELPER FUNCTIONS @@@@@@@@@ #


def test_is_even():
    assert(hackday.is_even(-2) is True)
    assert(hackday.is_even(-1) is False)
    assert(hackday.is_even(0) is True)
    assert(hackday.is_even(1) is False)
    assert(hackday.is_even(2) is True)
    assert(hackday.is_even(1.0) is False)
    assert(hackday.is_even(2.0) is True)


def test_parse_cidr():
    assert(hackday.parse_cidr("172.16.0.0/14") == "172.16.0.0", "14")
    assert(hackday.parse_cidr("0.0.0.0/1") == "0.0.0.0", "1")
    assert(hackday.parse_cidr("255.255.255.255/32") == "255.255.255.255", "32")


def test_calc_ip_int():
    assert(hackday.calc_ip_int("172.16.0.0") == 2886729728)
    assert(hackday.calc_ip_int("0.0.0.0") == 0)
    assert(hackday.calc_ip_int("255.255.255.255") == 4294967295)


def test_calc_scale_from_int():
    assert(hackday.calc_scale_from_int(2886729728, 24) == (2886729728, 2886729983))
    assert(hackday.calc_scale_from_int(0, 1) == (0, 2147483647))
    assert(hackday.calc_scale_from_int(4294967295, 32) == (4294967295, 4294967295))
