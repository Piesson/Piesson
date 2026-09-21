import hashlib
import tempfile
import unittest
from pathlib import Path

from tests import conftest  # noqa: F401
from update_readme_asset_versions import RAW_PREFIX, update_asset_versions


class ReadmeAssetVersionTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.assets = {}
        self.paths = [
            "profile-summary-card-output/default/0-profile-details.svg",
            "dashboard/weekly_dashboard.svg",
            "dashboard/progress_sparklines.svg",
        ]
        for index, relative in enumerate(self.paths):
            path = self.root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(f"svg-{index}".encode())
            self.assets[relative] = path

        self.readme = self.root / "README.md"
        self.readme.write_text(
            "\n".join(
                f'<img src="{RAW_PREFIX}{relative}">' for relative in self.paths
            )
            + "\n"
        )

    def tearDown(self):
        self.tmp.cleanup()

    def expected_version(self, relative):
        return hashlib.sha256(self.assets[relative].read_bytes()).hexdigest()[:12]

    def test_adds_content_hash_to_every_public_svg(self):
        self.assertTrue(update_asset_versions(self.readme, self.assets))
        content = self.readme.read_text()
        for relative in self.paths:
            self.assertIn(
                f"{RAW_PREFIX}{relative}?v={self.expected_version(relative)}",
                content,
            )

    def test_is_idempotent_until_asset_bytes_change(self):
        self.assertTrue(update_asset_versions(self.readme, self.assets))
        self.assertFalse(update_asset_versions(self.readme, self.assets))

        changed = self.paths[1]
        self.assets[changed].write_bytes(b"new-svg")
        self.assertTrue(update_asset_versions(self.readme, self.assets))
        self.assertIn(
            f"{RAW_PREFIX}{changed}?v={self.expected_version(changed)}",
            self.readme.read_text(),
        )

    def test_replaces_existing_version_instead_of_stacking_queries(self):
        update_asset_versions(self.readme, self.assets)
        self.assets[self.paths[0]].write_bytes(b"updated")
        update_asset_versions(self.readme, self.assets)
        content = self.readme.read_text()
        self.assertNotIn("?v=", content.splitlines()[0].split("?v=", 1)[1])

    def test_fails_closed_when_expected_readme_reference_is_missing(self):
        self.readme.write_text("# no assets\n")
        with self.assertRaisesRegex(ValueError, "does not reference"):
            update_asset_versions(self.readme, self.assets)


if __name__ == "__main__":
    unittest.main()
