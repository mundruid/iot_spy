"""Unit tests for sshdump module."""


"""Unit Test sshdump."""
import sys

from unittest.mock import patch
from io import StringIO

from iot_spy import sshdump


@patch(
    "iot_spy.sshdump.print_tcpdump",
)
def test_read_process_tcpdump(mock_print, sample_sshdump, sample_data):
    sys.stdin = sample_sshdump

    sshdump.read_process_tcpdump()

    mock_print.assert_called()
    assert mock_print.call_count == 6
    mock_print.assert_called_with(sample_data, 1630978241737502720)


@patch(
    "iot_spy.sshdump.print_tcpdump",
)
def test_read_process_tcpdump_no_print(mock_print, incomplete_sshdump):
    sys.stdin = incomplete_sshdump

    sshdump.read_process_tcpdump()

    mock_print.assert_not_called()
