"""Inspect saved Oculus Go Fastboot text. Never connects to a device."""

import argparse
import json
from pathlib import Path
import re


MAX_BYTES = 1024 * 1024
FIELDS = {
    'secure boot': 'secure_boot_reported',
    'secure': 'fastboot_secure_reported',
    'verity enabled': 'verity_reported',
    'verified boot enabled': 'verified_boot_reported',
    'device unlocked': 'bootloader_unlocked_reported',
    'device critical unlocked': 'critical_unlocked_reported',
}
LABELS = {'synthetic', 'historical'}
BOOL = {'true': True, 'false': False, 'yes': True, 'no': False}


class CaptureError(ValueError):
    """A capture is invalid or unsafe to interpret."""


def parse_capture(text):
    """Return only allowlisted metadata; never include raw input in messages."""
    records = {}

    def record(key, value):
        if key in records and records[key] != value:
            raise CaptureError(f'Conflicting values for {key}')
        records[key] = value

    for line in text.splitlines():
        line = re.sub(r'^\s*\(bootloader\)\s*', '', line, flags=re.IGNORECASE).strip()
        name, sep, raw = line.partition(':')
        if not sep:
            continue
        name, value = name.strip().casefold(), raw.strip().casefold()
        if name == '# evidence':
            if value not in LABELS:
                raise CaptureError('Invalid evidence label')
            record('source_label', value)
        elif name == 'product':
            if value != 'pacific':
                raise CaptureError('Product is not pacific')
            record('product', value)
        elif name in FIELDS:
            key = FIELDS[name]
            if value not in BOOL:
                raise CaptureError(f'Invalid boolean for {key}')
            record(key, BOOL[value])

    if not any(key in records for key in FIELDS.values()):
        raise CaptureError('No recognized boot-state flags; use the saved Fastboot replies')

    flags = {key: records.get(key) for key in FIELDS.values()}
    soc, fastboot = flags['secure_boot_reported'], flags['fastboot_secure_reported']
    if soc is not None and fastboot is not None and soc != fastboot:
        result = 'secure_indicators_disagree'
    elif records.get('product') is None:
        result = 'product_unconfirmed'
    elif soc is True and flags['bootloader_unlocked_reported'] is True:
        result = 'secure_boot_and_bootloader_unlock_both_reported'
    else:
        result = 'no_coexistence_established'

    return {'source_label': records.get('source_label', 'unspecified'),
            'product': records.get('product'), 'reported_flags': flags,
            'finding': result, 'hardware_root_of_trust_inferred': False}


def compare(left, right):
    changes = {}
    for key in FIELDS.values():
        old, new = left['reported_flags'][key], right['reported_flags'][key]
        status = ('missing_value' if old is None or new is None else
                  'same' if old == new else 'different')
        changes[key] = {'left': old, 'right': new, 'comparison': status}
    return {'left': left, 'right': right, 'comparison': changes,
            'same_device_or_transition_verified': False}


def load_capture(path):
    try:
        with path.open('rb') as stream:
            data = stream.read(MAX_BYTES + 1)
    except OSError:
        raise CaptureError('Cannot read capture file') from None
    if len(data) > MAX_BYTES:
        raise CaptureError('Capture exceeds 1 MiB')
    try:
        text = data.decode('utf-8-sig')
    except UnicodeDecodeError:
        raise CaptureError('Capture must be UTF-8 text') from None
    return parse_capture(text)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='action', required=True)
    sub.add_parser('inspect', help='summarize one saved text capture').add_argument('capture', type=Path)
    comparison = sub.add_parser('compare', help='compare two saved text captures')
    comparison.add_argument('left', type=Path)
    comparison.add_argument('right', type=Path)
    args = parser.parse_args(argv)
    try:
        if args.action == 'inspect':
            output = load_capture(args.capture)
        else:
            output = compare(load_capture(args.left), load_capture(args.right))
    except CaptureError as error:
        parser.exit(2, f'error: {error}\n')
    print(json.dumps(output, indent=2, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
