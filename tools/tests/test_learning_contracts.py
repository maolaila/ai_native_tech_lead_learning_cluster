"""检查已知的学习契约：真实注解有解释、示例表名存在；不是全面语义审查。"""
import importlib.util
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('scanner', ROOT / 'tools/java_source_scan.py')
scanner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(scanner)


class LearningContractTest(unittest.TestCase):
    def test_annotation_scanner_ignores_comments_literals_and_preserves_lines(self):
        source = '// @Service\n/** @Entity */\nString s = "@Fake";\n@org.example.NotNull @Valid String x;\n'
        self.assertEqual(list(scanner.annotations(source)), [('NotNull', 4), ('Valid', 4)])

    def test_annotation_scanner_ignores_text_blocks(self):
        source = 'String sql = """\n @Fake\n """;\n@Test\nvoid test() {}\n'
        self.assertEqual(list(scanner.annotations(source)), [('Test', 4)])

    def test_all_actual_annotations_are_explained_locally(self):
        dictionary = (ROOT / 'mini-commerce/docs/SPRING-JAVA-ANNOTATIONS.md').read_text()
        names = set()
        for source in (ROOT / 'mini-commerce/backend/src').rglob('*.java'):
            names.update(name for name, _ in scanner.annotations(source.read_text()))
        self.assertTrue(names)
        self.assertEqual(sorted(name for name in names if '@' + name not in dictionary), [])

    def test_permission_probe_names_exist_in_real_migrations(self):
        sql = '\n'.join(p.read_text() for p in (ROOT / 'mini-commerce/backend/src/main/resources/db/migration').glob('*.sql'))
        known_tables = set(re.findall(r'create\s+table\s+(?:if\s+not\s+exists\s+)?(\w+)', sql, re.I))
        probe = (ROOT / 'mini-commerce/scripts/check_mcp_runtime.py').read_text()
        names = re.findall(r"has_table_privilege\(current_user, 'public\.(\w+)'", probe)
        self.assertTrue(names, '权限探针必须实际检查表权限，不能删除断言来让检查通过')
        self.assertTrue({'orders', 'app_users', 'refresh_tokens'}.issubset(names))
        self.assertTrue(set(names).issubset(known_tables), set(names) - known_tables)

    def test_entry_does_not_present_tests_as_request_execution_stage(self):
        guide = (ROOT / 'mini-commerce/docs/BEGINNER-START-HERE.md').read_text()
        self.assertNotIn('→ 测试证明规则没有被破坏', guide)
        self.assertIn('不是每个用户请求', guide)


if __name__ == '__main__':
    unittest.main()
