import unittest
from prepare_thread_migration import migrate

class MigrationTests(unittest.TestCase):
    def test_explicit_binding_preserves_native_session_and_other_platforms(self):
        mapping = {'slack:123.456': 'native-a', 'discord:123.456': 'native-b'}
        meta = {'slack:123.456': '/workspace/a'}
        result, metadata = migrate(mapping, meta, [{'team':'T1','channel':'C1','thread':'123.456'}])
        self.assertEqual(result, {'slack:T1:C1:123.456':'native-a','discord:123.456':'native-b'})
        self.assertEqual(metadata, {'slack:T1:C1:123.456':'/workspace/a'})
        self.assertIn('slack:123.456', mapping)
    def test_conflicting_destination_fails(self):
        with self.assertRaises(ValueError):
            migrate({'slack:123.456':'a','slack:T1:C1:123.456':'b'}, {}, [{'team':'T1','channel':'C1','thread':'123.456'}])
    def test_cannot_guess_same_timestamp_ownership(self):
        with self.assertRaises(ValueError):
            migrate({'slack:123.456':'a'}, {}, [{'team':'T1','channel':'C1','thread':'123.456'}, {'team':'T1','channel':'C2','thread':'123.456'}])
    def test_float_timestamp_rejected(self):
        with self.assertRaises(ValueError):
            migrate({'slack:123.456':'a'}, {}, [{'team':'T1','channel':'C1','thread':123.456}])
    def test_missing_or_malformed_source_rejected(self):
        with self.assertRaises(ValueError):
            migrate({}, {}, [{'team':'T1','channel':'C1','thread':'123.456'}])
        with self.assertRaises(ValueError):
            migrate({'slack:123.456':42}, {}, [])

if __name__ == '__main__':
    unittest.main()
