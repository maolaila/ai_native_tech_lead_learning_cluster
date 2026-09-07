"""文档构建目标路径的回归测试，不需要安装 MkDocs。"""

import importlib.util
import tempfile
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location(
    "builder", Path(__file__).parents[1] / "build_docs_site.py"
)
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)


class OutputSafetyTest(unittest.TestCase):
    def test_rejects_repository_and_ancestors(self):
        with tempfile.TemporaryDirectory() as folder:
            repo = Path(folder) / "repo"
            repo.mkdir()
            for unsafe in [repo, repo / "site", repo.parent, Path(repo.anchor)]:
                with self.assertRaises(ValueError):
                    builder.validate_output(unsafe, repo)

    def test_rejects_unowned_nonempty_folder(self):
        with tempfile.TemporaryDirectory() as folder:
            repo, output = Path(folder) / "repo", Path(folder) / "existing"
            repo.mkdir()
            output.mkdir()
            (output / "important.txt").write_text("keep")
            with self.assertRaises(ValueError):
                builder.validate_output(output, repo)
            self.assertEqual((output / "important.txt").read_text(), "keep")

    def test_allows_new_or_owned_output(self):
        with tempfile.TemporaryDirectory() as folder:
            repo, output = Path(folder) / "repo", Path(folder) / "site"
            repo.mkdir()
            marker = builder.validate_output(output, repo)
            output.mkdir()
            (output / "index.html").write_text("site")
            marker.write_text(str(repo.resolve()))
            self.assertEqual(builder.validate_output(output, repo), marker)

    def test_resolves_symlink_before_check(self):
        with tempfile.TemporaryDirectory() as folder:
            repo, alias = Path(folder) / "repo", Path(folder) / "alias"
            repo.mkdir()
            alias.symlink_to(repo, target_is_directory=True)
            with self.assertRaises(ValueError):
                builder.validate_output(alias, repo)


if __name__ == "__main__":
    unittest.main()
