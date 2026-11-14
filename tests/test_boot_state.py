import contextlib
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from boot_state import CaptureError, MAX_BYTES, compare, load_capture, main, parse_capture


class BootState(unittest.TestCase):
    def test_curated_historical_observation(self):
        record = load_capture(ROOT / 'examples/pacific-observed.txt')
        self.assertEqual(record['source_label'], 'historical')
        self.assertEqual(record['finding'], 'secure_boot_and_bootloader_unlock_both_reported')
        self.assertIs(record['hardware_root_of_trust_inferred'], False)

    def test_comparison_does_not_claim_real_transition(self):
        left = load_capture(ROOT / 'examples/pacific-locked-synthetic.txt')
        right = load_capture(ROOT / 'examples/pacific-observed.txt')
        result = compare(left, right)
        self.assertEqual(result['left']['source_label'], 'synthetic')
        self.assertEqual(result['comparison']['bootloader_unlocked_reported']['comparison'], 'different')
        self.assertEqual(result['comparison']['secure_boot_reported']['comparison'], 'same')
        self.assertIs(result['same_device_or_transition_verified'], False)

    def test_secure_indicators_disagree(self):
        record = parse_capture('product: pacific\nsecure: no\nSecure boot: true\nDevice unlocked: true')
        self.assertEqual(record['finding'], 'secure_indicators_disagree')
        self.assertIs(record['reported_flags']['secure_boot_reported'], True)
        self.assertIs(record['reported_flags']['fastboot_secure_reported'], False)

    def test_missing_value_is_not_false(self):
        record = parse_capture('product: pacific\nsecure: yes\nDevice unlocked: true')
        self.assertIsNone(record['reported_flags']['secure_boot_reported'])
        self.assertEqual(record['finding'], 'no_coexistence_established')
        self.assertEqual(compare(record, record)['comparison']['verity_reported']['comparison'], 'missing_value')

    def test_missing_product_is_not_confirmed(self):
        record = parse_capture('Secure boot: true\nDevice unlocked: true')
        self.assertEqual(record['finding'], 'product_unconfirmed')
        self.assertEqual(record['source_label'], 'unspecified')

    def test_reported_false_does_not_attest_hardware(self):
        record = parse_capture('product: pacific\nsecure: no\nSecure boot: false\nDevice unlocked: true')
        self.assertIs(record['reported_flags']['secure_boot_reported'], False)
        self.assertIs(record['hardware_root_of_trust_inferred'], False)
        self.assertEqual(record['finding'], 'no_coexistence_established')

    def test_other_product_rejected_without_reflecting_input(self):
        with self.assertRaisesRegex(CaptureError, '^Product is not pacific$'):
            parse_capture('product: an-identifier\nsecure: yes')

    def test_conflicting_duplicates_are_rejected(self):
        with self.assertRaisesRegex(CaptureError, '^Conflicting values for secure_boot_reported$'):
            parse_capture('(bootloader) Secure boot: true\nSecure boot: false')

    def test_bool_normalization_and_matching_duplicates(self):
        record = parse_capture('Product: PACIFIC\r\n (BOOTLOADER) \tSecure boot: TRUE\r\nSecure boot: yes')
        self.assertIs(record['reported_flags']['secure_boot_reported'], True)

    def test_identifier_fields_are_ignored(self):
        record = parse_capture('product: pacific\nserialno: PRIVATE-IDENTIFIER\n'
                               '(bootloader) Device unlock serial number: SECOND-IDENTIFIER\nsecure: yes')
        self.assertNotIn('IDENTIFIER', json.dumps(record))

    def test_invalid_booleans_and_labels_rejected(self):
        for raw in ('Secure boot: secret', '# evidence: secret\nsecure: yes'):
            with self.subTest(raw=raw), self.assertRaises(CaptureError) as error:
                parse_capture(raw)
            self.assertNotIn('secret', str(error.exception))

    def test_empty_or_unrecognized_report_rejected(self):
        with self.assertRaises(CaptureError):
            parse_capture('product: pacific\nOKAY')

    def test_file_limits_and_encoding(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / 'capture.txt'
            for data in (b'x' * (MAX_BYTES + 1), b'\xff'):
                path.write_bytes(data)
                with self.assertRaises(CaptureError):
                    load_capture(path)
            path.write_bytes(b'\xef\xbb\xbfproduct: pacific\nsecure: yes')
            self.assertEqual(load_capture(path)['product'], 'pacific')

    def test_cli_output_is_json(self):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            self.assertEqual(main(['inspect', str(ROOT / 'examples/pacific-observed.txt')]), 0)
        self.assertEqual(json.loads(output.getvalue())['source_label'], 'historical')


if __name__ == '__main__':
    unittest.main()
