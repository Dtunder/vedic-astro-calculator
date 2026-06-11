import unittest
from unittest.mock import MagicMock

from resilience import retry_with_fallback


class TestResilience(unittest.TestCase):
    def test_retry_success_first_try(self) -> None:
        mock_func = MagicMock(return_value="success")
        decorated_func = retry_with_fallback(retries=3, delay=0.01)(mock_func)

        result = decorated_func()
        self.assertEqual(result, "success")
        self.assertEqual(mock_func.call_count, 1)

    def test_retry_success_after_failures(self) -> None:
        mock_func = MagicMock(
            side_effect=[ValueError("error"), ValueError("error"), "success"]
        )
        decorated_func = retry_with_fallback(
            retries=3, delay=0.01, exceptions=(ValueError,)
        )(mock_func)

        result = decorated_func()
        self.assertEqual(result, "success")
        self.assertEqual(mock_func.call_count, 3)

    def test_retry_exhausted_raises_exception_no_fallback(self) -> None:
        mock_func = MagicMock(side_effect=ValueError("error"))
        decorated_func = retry_with_fallback(
            retries=2, delay=0.01, exceptions=(ValueError,)
        )(mock_func)

        with self.assertRaises(ValueError):
            decorated_func()
        self.assertEqual(mock_func.call_count, 3)  # 1 initial + 2 retries

    def test_retry_exhausted_calls_fallback(self) -> None:
        mock_func = MagicMock(side_effect=ValueError("error"))
        fallback_func = MagicMock(return_value="fallback_result")
        decorated_func = retry_with_fallback(
            retries=2,
            delay=0.01,
            exceptions=(ValueError,),
            fallback=fallback_func,
        )(mock_func)

        result = decorated_func("arg1", kwarg1="val1")
        self.assertEqual(result, "fallback_result")
        self.assertEqual(mock_func.call_count, 3)
        fallback_func.assert_called_once_with("arg1", kwarg1="val1")

    def test_unhandled_exception_raises_immediately(self) -> None:
        mock_func = MagicMock(side_effect=TypeError("unhandled"))
        decorated_func = retry_with_fallback(
            retries=3, delay=0.01, exceptions=(ValueError,)
        )(mock_func)

        with self.assertRaises(TypeError):
            decorated_func()
        self.assertEqual(mock_func.call_count, 1)


if __name__ == "__main__":
    unittest.main()
