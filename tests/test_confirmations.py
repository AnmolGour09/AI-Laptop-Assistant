import asyncio
import time
import unittest
from types import SimpleNamespace
from pathlib import Path
from unittest.mock import AsyncMock, Mock, patch

from Jarvis_confirmations import (
    _PendingAction,
    _stage_action,
    _confirmation_error,
    _normalize_phrase,
    _states,
    clear_session_confirmation_state,
    confirm_pending_action,
    prepare_email,
    record_user_transcript,
)
from Jarvis_browser import open_youtube_in_brave
from Jarvis_system_control import perform_system_action
from Jarvis_window_CTRL import _resolve_app_command, folder_file, open as open_app
from keyboard_mouse_CTRL import SafeController
from agent import INTRO_INSTRUCTIONS, speak_session_intro


class ConfirmationTests(unittest.TestCase):
    def setUp(self) -> None:
        _states.clear()

    def tearDown(self) -> None:
        _states.clear()

    def test_confirmation_requires_action_specific_phrase(self) -> None:
        self.assertIsNone(_confirmation_error(
            "email",
            "Confirm email.",
            2,
            _PendingAction("email", {}, 1, time.monotonic()),
            time.monotonic(),
        ))
        self.assertEqual(
            _confirmation_error(
                "email",
                "yes",
                2,
                _PendingAction("email", {}, 1, time.monotonic()),
                time.monotonic(),
            ),
            "mismatch",
        )

    def test_confirmation_must_be_a_new_user_turn(self) -> None:
        pending = _PendingAction("shutdown", {}, 3, time.monotonic())
        self.assertEqual(
            _confirmation_error("shutdown", "confirm shutdown", 3, pending, time.monotonic()),
            "missing",
        )

    def test_staging_email_does_not_send_and_requires_a_new_exact_confirmation(self) -> None:
        session = object()
        ctx = SimpleNamespace(session=session)
        key = id(session)

        draft = asyncio.run(
            prepare_email.__wrapped__("user@example.com", "Hello", "Private body", ctx)
        )
        self.assertIn("Nothing has been done yet", draft)

        with patch("Jarvis_confirmations.send_email_now") as send:
            record_user_transcript(key, "yes", is_final=True)
            result = asyncio.run(confirm_pending_action.__wrapped__(ctx))
        self.assertIn("Confirmation not recognized", result)
        send.assert_not_called()

    def test_exact_new_confirmation_runs_only_the_confirmed_system_action(self) -> None:
        session = object()
        ctx = SimpleNamespace(session=session)
        key = id(session)
        _stage_action(key, "shutdown", {})
        record_user_transcript(key, "confirm shutdown", is_final=True)

        with patch(
            "Jarvis_confirmations.perform_system_action",
            return_value="Windows accepted the shutdown request.",
        ) as perform:
            result = asyncio.run(confirm_pending_action.__wrapped__(ctx))

        self.assertEqual(result, "Windows accepted the shutdown request.")
        perform.assert_called_once_with("shutdown")

    def test_expired_confirmation_is_rejected(self) -> None:
        pending = _PendingAction("restart", {}, 1, time.monotonic() - 121)
        self.assertEqual(
            _confirmation_error("restart", "confirm restart", 2, pending, time.monotonic()),
            "expired",
        )

    def test_user_transcripts_and_state_are_session_scoped(self) -> None:
        record_user_transcript(10, "confirm email", is_final=False)
        self.assertNotIn(10, _states)

        record_user_transcript(10, "confirm email", is_final=True)
        record_user_transcript(20, "cancel", is_final=True)
        self.assertEqual(_states[10].transcript, "confirm email")
        self.assertEqual(_states[20].transcript, "cancel")

        clear_session_confirmation_state(10)
        self.assertNotIn(10, _states)
        self.assertIn(20, _states)

    def test_normalization_is_case_and_punctuation_insensitive(self) -> None:
        self.assertEqual(_normalize_phrase("  Confirm Email!  "), "confirm email")

    def test_system_command_requires_windows_and_uses_allowlist(self) -> None:
        with patch("Jarvis_system_control.platform.system", return_value="Windows"), patch(
            "Jarvis_system_control.subprocess.run"
        ) as run:
            self.assertEqual(perform_system_action("unexpected"), "Unsupported system action: unexpected.")
            run.assert_not_called()

            self.assertEqual(perform_system_action("shutdown"), "Windows accepted the shutdown request.")
            run.assert_called_once_with(
                ["shutdown", "/s", "/t", "0"],
                check=True,
                timeout=15,
                capture_output=True,
                text=True,
            )

    def test_file_deletion_is_blocked_without_scanning_or_removing(self) -> None:
        result = asyncio.run(folder_file.__wrapped__("delete my report"))
        self.assertIn("Nothing was deleted", result)

    def test_app_launch_only_resolves_configured_names(self) -> None:
        with patch("Jarvis_window_CTRL.shutil.which", return_value="calc.exe"):
            self.assertEqual(_resolve_app_command("calculator"), ["calc.exe"])
            self.assertEqual(_resolve_app_command("calculator & shutdown"), [])

        with patch("Jarvis_window_CTRL.asyncio.create_subprocess_exec") as launch:
            result = asyncio.run(open_app.__wrapped__("notepad & shutdown"))
        self.assertIn("Unsupported", result)
        launch.assert_not_called()

    def test_typed_text_is_not_written_to_the_control_log_or_result(self) -> None:
        controller = SafeController.__new__(SafeController)
        controller.active = True
        controller.keyboard = Mock()
        controller.log = Mock()

        result = asyncio.run(controller.type_text("private message"))

        self.assertNotIn("private message", result)
        self.assertNotIn("private message", str(controller.log.call_args))
        controller.keyboard.press.assert_called()
        controller.keyboard.release.assert_called()

    def test_youtube_search_opens_brave_results_without_selecting_a_video(self) -> None:
        with patch("Jarvis_browser.platform.system", return_value="Windows"), patch(
            "Jarvis_browser.find_brave_executable",
            return_value=Path(r"C:\Apps\Brave\brave.exe"),
        ), patch("Jarvis_browser.subprocess.Popen") as launch:
            result = asyncio.run(
                open_youtube_in_brave.__wrapped__("Java interview questions")
            )

        self.assertIn("Choose the video you want manually", result)
        args = launch.call_args.args[0]
        self.assertEqual(args[0], r"C:\Apps\Brave\brave.exe")
        self.assertIn("results?search_query=Java+interview+questions", args[1])

    def test_youtube_home_opens_brave_without_confirmation(self) -> None:
        with patch("Jarvis_browser.platform.system", return_value="Windows"), patch(
            "Jarvis_browser.find_brave_executable",
            return_value=Path(r"C:\Apps\Brave\brave.exe"),
        ), patch("Jarvis_browser.subprocess.Popen") as launch:
            result = asyncio.run(open_youtube_in_brave.__wrapped__())

        self.assertIn("Choose a video manually", result)
        self.assertEqual(launch.call_args.args[0][1], "https://www.youtube.com/")

    def test_youtube_search_reports_missing_brave_instead_of_using_another_browser(self) -> None:
        with patch("Jarvis_browser.platform.system", return_value="Windows"), patch(
            "Jarvis_browser.find_brave_executable", return_value=None
        ), patch("Jarvis_browser.subprocess.Popen") as launch:
            result = asyncio.run(open_youtube_in_brave.__wrapped__("Python"))

        self.assertIn("Brave was not found", result)
        launch.assert_not_called()

    def test_intro_uses_realtime_reply_not_unsupported_session_say(self) -> None:
        class Speech:
            def __await__(self):
                async def complete():
                    return self

                return complete().__await__()

            def exception(self):
                return None

        session = Mock()
        session.generate_reply.return_value = Speech()
        publish_status = AsyncMock()

        result = asyncio.run(speak_session_intro(session, publish_status))

        self.assertTrue(result)
        session.generate_reply.assert_called_once_with(
            instructions=INTRO_INSTRUCTIONS,
            tool_choice="none",
        )
        session.say.assert_not_called()
        publish_status.assert_awaited_once_with("intro_complete")

    def test_intro_failure_does_not_claim_intro_complete(self) -> None:
        class Speech:
            def __await__(self):
                async def complete():
                    return self

                return complete().__await__()

            def exception(self):
                return RuntimeError("model failed")

        session = Mock()
        session.generate_reply.return_value = Speech()
        publish_status = AsyncMock()

        result = asyncio.run(speak_session_intro(session, publish_status))

        self.assertFalse(result)
        publish_status.assert_awaited_once_with("intro_failed")


if __name__ == "__main__":
    unittest.main()
