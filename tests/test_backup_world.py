import importlib.util
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


MODULE_PATH = (
    Path(__file__).resolve().parents[1]
    / "scripts/backup/backup-world.py"
)

spec = importlib.util.spec_from_file_location(
    "blocktopia_backup_world", MODULE_PATH
)
backup = importlib.util.module_from_spec(spec)
spec.loader.exec_module(backup)


class TestBackupWorld(unittest.TestCase):

    def sample_response(self):
        return (
            "[INFO] Data saved. Files are now ready to be copied.\n"
            "Blocktopia/db/000015.log:20, "
            "Blocktopia/db/CURRENT:4, "
            "Blocktopia/level.dat:5, "
            "Blocktopia/levelname.txt:10\n"
        )

    def test_parse_bedrock_response(self):
        files = backup.parse_file_list(
            self.sample_response()
        )

        self.assertEqual(len(files), 4)
        self.assertEqual(
            files[Path("Blocktopia/db/000015.log")], 20
        )

    def test_response_not_ready(self):
        files = backup.parse_file_list(
            "[INFO] Saving...\n"
        )
        self.assertIsNone(files)

    def test_reject_missing_essential_files(self):
        response = (
            "[INFO] Data saved. Files are now ready to be copied.\n"
            "Blocktopia/db/CURRENT:4\n"
        )
        with self.assertRaises(ValueError):
            backup.parse_file_list(response)

    def test_reject_invalid_file_size(self):
        response = self.sample_response().replace(
            "level.dat:5", "level.dat:abc"
        )
        with self.assertRaises(ValueError):
            backup.parse_file_list(response)

    def test_reject_duplicate_file(self):
        response = self.sample_response().replace(
            "Blocktopia/levelname.txt:10",
            "Blocktopia/db/CURRENT:4"
        )
        with self.assertRaises(ValueError):
            backup.parse_file_list(response)

    def test_copy_exact_reported_size(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            data = root / "data"
            source = data / "worlds/Blocktopia/db"
            source.mkdir(parents=True)

            (source / "CURRENT").write_bytes(
                b"ABCDEFGHIJ"
            )

            destination = root / "backup"

            with patch.object(backup, "DATA", data):
                backup.copy_files(
                    {Path("Blocktopia/db/CURRENT"): 4},
                    destination,
                )

            result = (
                destination / "Blocktopia/db/CURRENT"
            ).read_bytes()

            self.assertEqual(result, b"ABCD")

    def test_reject_source_smaller_than_expected(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            data = root / "data"
            source = data / "worlds/Blocktopia/db"
            source.mkdir(parents=True)

            (source / "CURRENT").write_bytes(b"ABC")

            with patch.object(backup, "DATA", data):
                with self.assertRaises(ValueError):
                    backup.copy_files(
                        {Path("Blocktopia/db/CURRENT"): 10},
                        root / "backup",
                    )

    def test_reject_symbolic_link(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            data = root / "data"
            source = data / "worlds/Blocktopia/db"
            source.mkdir(parents=True)

            actual = root / "actual"
            actual.write_bytes(b"ABCD")
            (source / "CURRENT").symlink_to(actual)

            with patch.object(backup, "DATA", data):
                with self.assertRaises(ValueError):
                    backup.copy_files(
                        {Path("Blocktopia/db/CURRENT"): 4},
                        root / "backup",
                    )


    def test_sigterm_triggers_interruption(self):
        import signal

        with self.assertRaises(InterruptedError):
            backup.handle_shutdown(signal.SIGTERM, None)

    def test_sigint_triggers_interruption(self):
        import signal

        with self.assertRaises(InterruptedError):
            backup.handle_shutdown(signal.SIGINT, None)


    def test_copy_failure_attempts_save_resume(self):
        """Falha na cópia não pode deixar de tentar liberar o mundo."""
        from unittest.mock import call

        sent = []

        def fake_run(args):
            if "--format" in args:
                if "{{.State.Running}}" in args:
                    return "true\n"
                return f"{backup.DATA} -> /data\n"
            raise AssertionError(f"Comando externo inesperado: {args}")

        def fake_send(command):
            sent.append(command)

        with tempfile.TemporaryDirectory() as temp:
            with (
                patch.object(backup, "BACKUPS", Path(temp)),
                patch.object(backup, "run", side_effect=fake_run),
                patch.object(backup, "send", side_effect=fake_send),
                patch.object(
                    backup,
                    "logs",
                    return_value=self.sample_response(),
                ),
                patch.object(backup.time, "sleep"),
                patch.object(backup, "copy_files",
                             side_effect=IOError("Falha simulada")),
                patch.object(backup, "wait_for", return_value=True),
            ):
                with self.assertRaises(IOError):
                    backup.main()

        self.assertEqual(
            sent,
            ["save hold", "save query", "save resume"],
        )


if __name__ == "__main__":
    unittest.main()
