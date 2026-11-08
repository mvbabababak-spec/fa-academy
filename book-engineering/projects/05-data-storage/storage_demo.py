"""Tiny temporary binary file: float32 payload, not a hardware benchmark."""
from pathlib import Path
from tempfile import TemporaryDirectory
import struct


def main():
    values = (1.0, 2.5, -3.0, 4.0)
    payload = struct.pack('<4f', *values)
    with TemporaryDirectory() as folder:
        path = Path(folder) / 'sample.bin'
        path.write_bytes(payload)
        raw = path.read_bytes()
        recovered = struct.unpack('<4f', raw)
        print(f'number_of_values={len(values)}')
        print(f'bytes_per_value={struct.calcsize("<f")}')
        print(f'payload_bytes={len(payload)}')
        print(f'file_bytes={path.stat().st_size}')
        print(f'recovered={recovered}')
        assert recovered == values


if __name__ == '__main__':
    main()
