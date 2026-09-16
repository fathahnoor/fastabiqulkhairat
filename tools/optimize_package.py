"""Build a lossless storage candidate and audit AOD without changing display data.

This cannot measure battery use or change the firmware's refresh scheduler.
Run after build.py. The standard BIN is retained as the comparison/fallback.
"""
import hashlib
import json
import struct
from pathlib import Path

from trexpro_wf import (decode_image, ids_to_names, pack, unpack,
                       validate_image_references, validate_trexpro_container)

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'out'


def referenced_images(node):
    result = set()
    if isinstance(node, dict):
        if 'ImageIndex' in node:
            result.update(range(node['ImageIndex'] - 1,
                                node['ImageIndex'] - 1 + node.get('ImagesCount', 1)))
        if 'BackgroundImageIndex' in node:
            result.add(node['BackgroundImageIndex'] - 1)
        for value in node.values():
            result.update(referenced_images(value))
    elif isinstance(node, list):
        for value in node:
            result.update(referenced_images(value))
    return result


def main():
    baseline = (OUT / 'fastabiqulkhairat.bin').read_bytes()
    params, images, _ = unpack(baseline)
    named = ids_to_names(params)
    # Refuse to silently change an unexpected build or target.
    before_container = validate_trexpro_container(baseline)
    idle = named['IdleScreen']
    assert set(idle) == {'Time', 'Date', 'Data', 'BackgroundImageIndex'}
    assert [entry['Type'] for entry in idle['Time']['Digital']['HoursMinutesSeconds']] == [0, 1]
    assert [entry['Type'] for entry in idle['Data']] == [
        'Steps', 'HeartRate', 'Battery', 'Weather', 'Weather']

    candidate = pack(params, images, compress=True, deduplicate_images=True)
    after_container = validate_trexpro_container(candidate)
    after_params, after_images, _ = unpack(candidate)
    assert after_params == params
    assert after_images == images  # Includes every weather state, alpha, and preview.
    validate_image_references(ids_to_names(after_params), after_images)
    assert len(candidate) < len(baseline)
    (OUT / 'fastabiqulkhairat-optimized.bin').write_bytes(candidate)

    aod_ids = referenced_images(idle)
    aod_blobs = [images[i] for i in sorted(aod_ids)]
    # Check the full image decoder too, not only compressed byte equality.
    for before, after in zip(images, after_images):
        assert decode_image(before) == decode_image(after)
    raw_before = struct.unpack_from('<I', baseline, 32)[0]
    raw_after = struct.unpack_from('<I', candidate, 32)[0]
    report = {
        'baseline_sha256': hashlib.sha256(baseline).hexdigest(),
        'candidate_sha256': hashlib.sha256(candidate).hexdigest(),
        'baseline_bytes': len(baseline), 'candidate_bytes': len(candidate),
        'file_bytes_saved': len(baseline) - len(candidate),
        'file_reduction_percent': round(100 * (1-len(candidate)/len(baseline)), 2),
        'expanded_body_before_bytes': raw_before, 'expanded_body_after_bytes': raw_after,
        'expanded_body_saved_bytes': raw_before-raw_after,
        'logical_images': len(images), 'physical_images_before': len(images),
        'physical_images_after': len(set(images)),
        'aod_referenced_images': len(aod_blobs), 'aod_unique_images': len(set(aod_blobs)),
        'aod_duplicate_blob_bytes': sum(map(len, aod_blobs))-sum(map(len, set(aod_blobs))),
        'parameter_identity': True, 'image_blob_identity': True, 'max_pixel_delta': 0,
        'baseline_container': before_container, 'candidate_container': after_container,
        'aod_audit': {
            'time_components': ['hour', 'minute'], 'seconds_component': False,
            'animation_component': False, 'custom_executable_code': False,
            'static_artwork_baked_in_background': True,
            'brightness_transforms_at_build_time': True,
            'refresh_schedule': 'Firmware controlled; not measured or changed',
            'sensor_sampling': 'No SDK sensor polling code in this declarative package',
            'display_and_data_fields_changed': False,
        },
        'device_compatibility_verified': False, 'battery_saving_measured': False,
        'interpretation': 'Storage and expanded package size only. Not a measurement of '
                          'runtime RAM, redraw work, wakeups, or battery life. Shared '
                          'offsets require a physical device compatibility check.',
    }
    (OUT / 'power-audit.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
