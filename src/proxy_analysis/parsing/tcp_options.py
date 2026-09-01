"""Parse raw TCP option kind/length/value tuples without feature inference."""

from __future__ import annotations

from dataclasses import dataclass
import struct


@dataclass(frozen=True, slots=True)
class TcpOption:
    kind: int
    value: bytes
    valid: bool = True


def parse_tcp_options(data: bytes) -> tuple[TcpOption, ...]:
    options: list[TcpOption] = []
    offset = 0
    while offset < len(data):
        kind = data[offset]
        if kind == 0:
            options.append(TcpOption(0, b""))
            break
        if kind == 1:
            options.append(TcpOption(1, b""))
            offset += 1
            continue
        if offset + 2 > len(data):
            options.append(TcpOption(kind, b"", False))
            break
        length = data[offset + 1]
        if length < 2 or offset + length > len(data):
            options.append(TcpOption(kind, data[offset + 2 :], False))
            break
        options.append(TcpOption(kind, data[offset + 2 : offset + length]))
        offset += length
    return tuple(options)


def tcp_option_values(data: bytes) -> dict[str, object]:
    parsed = parse_tcp_options(data)
    result: dict[str, object] = {
        "valid": all(item.valid for item in parsed),
        "kinds": [item.kind for item in parsed],
        "mss": None,
        "window_scale": None,
        "sack_permitted": False,
        "timestamps": None,
    }
    for item in parsed:
        if not item.valid:
            continue
        if item.kind == 2 and len(item.value) == 2:
            result["mss"] = struct.unpack("!H", item.value)[0]
        elif item.kind == 3 and len(item.value) == 1:
            result["window_scale"] = item.value[0]
        elif item.kind == 4 and len(item.value) == 0:
            result["sack_permitted"] = True
        elif item.kind == 8 and len(item.value) == 8:
            result["timestamps"] = struct.unpack("!II", item.value)
    return result

