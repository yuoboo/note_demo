from utils.time_cal import get_today_start_and_end_datetime


def test_get_today_start_and_end_datetime():
    assert len(get_today_start_and_end_datetime()) == 2
