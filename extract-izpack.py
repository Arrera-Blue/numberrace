#!/usr/bin/env python3
"""Extract Linux application files from an IzPack installer JAR without Java.

Reads the Java-serialized PackFile streams inside ``packs/pack-Core Windows/Linux``
and ``packs/pack-French`` from the Number Race IzPack installer JAR and writes
the extracted files into the target directory.
"""

import io
import os
import struct
import sys
import zipfile


class JavaObjectStream:
    """Minimal Java ObjectInputStream reader for IzPack PackFile streams."""

    TC_NULL = 0x70
    TC_REFERENCE = 0x71
    TC_CLASSDESC = 0x72
    TC_OBJECT = 0x73
    TC_STRING = 0x74
    TC_ARRAY = 0x75
    TC_CLASS = 0x76
    TC_BLOCKDATA = 0x77
    TC_ENDBLOCKDATA = 0x78
    TC_RESET = 0x79
    TC_BLOCKDATALONG = 0x7A
    TC_LONGSTRING = 0x7C
    BASE_WIRE_HANDLE = 0x7E0000
    SC_WRITE_METHOD = 0x01

    def __init__(self, data: bytes) -> None:
        self.f = io.BytesIO(data)
        magic, version = struct.unpack(">HH", self.f.read(4))
        if magic != 0xACED or version != 5:
            raise ValueError(f"Invalid Java serialization header: {magic:#x} v{version}")
        self.handles: list[object] = []
        self._block_buf = b""

    def _register(self, obj: object) -> int:
        self.handles.append(obj)
        return len(self.handles) - 1

    def _u1(self) -> int:
        return struct.unpack(">B", self.f.read(1))[0]

    def _u2(self) -> int:
        return struct.unpack(">H", self.f.read(2))[0]

    def _i4(self) -> int:
        return struct.unpack(">i", self.f.read(4))[0]

    def _i8(self) -> int:
        return struct.unpack(">q", self.f.read(8))[0]

    def _utf(self) -> str:
        return self.f.read(self._u2()).decode("utf-8", "replace")

    def _long_utf(self) -> str:
        return self.f.read(self._i8()).decode("utf-8", "replace")

    def read_block_bytes(self, n: int) -> bytes:
        out = bytearray()
        while len(out) < n:
            if not self._block_buf:
                tc = self._u1()
                if tc == self.TC_BLOCKDATA:
                    self._block_buf = self.f.read(self._u1())
                elif tc == self.TC_BLOCKDATALONG:
                    self._block_buf = self.f.read(self._i4())
                else:
                    raise ValueError(
                        f"Expected blockdata token, got {tc:#x} at {self.f.tell()}"
                    )
            take = min(n - len(out), len(self._block_buf))
            out.extend(self._block_buf[:take])
            self._block_buf = self._block_buf[take:]
        return bytes(out)

    def read_block_int(self) -> int:
        return struct.unpack(">i", self.read_block_bytes(4))[0]

    def _read_classdesc(self) -> dict | None:
        tc = self._u1()
        if tc == self.TC_NULL:
            return None
        if tc == self.TC_REFERENCE:
            return self.handles[self._i4() - self.BASE_WIRE_HANDLE]  # type: ignore[return-value]
        if tc != self.TC_CLASSDESC:
            raise ValueError(f"Expected classdesc token, got {tc:#x}")

        name = self._utf()
        self._i8()  # serialVersionUID
        idx = self._register(None)
        flags = self._u1()
        num_fields = self._u2()
        fields = []
        for _ in range(num_fields):
            ftype = chr(self._u1())
            fname = self._utf()
            if ftype in ("L", "["):
                self.read_object()
            fields.append((ftype, fname))
        while True:
            atc = self._u1()
            if atc == self.TC_ENDBLOCKDATA:
                break
            raise ValueError(f"Unexpected class annotation token: {atc:#x}")
        super_cd = self._read_classdesc()
        cd = {"name": name, "flags": flags, "fields": fields, "super": super_cd}
        self.handles[idx] = cd
        return cd

    def _read_fields(self, cd: dict) -> dict:
        vals: dict = {}
        if cd["super"]:
            vals.update(self._read_fields(cd["super"]))
        for ftype, fname in cd["fields"]:
            if ftype == "Z":
                vals[fname] = bool(self._u1())
            elif ftype == "B":
                vals[fname] = struct.unpack(">b", self.f.read(1))[0]
            elif ftype == "C":
                vals[fname] = self._u2()
            elif ftype == "S":
                vals[fname] = struct.unpack(">h", self.f.read(2))[0]
            elif ftype == "I":
                vals[fname] = self._i4()
            elif ftype == "J":
                vals[fname] = self._i8()
            elif ftype == "F":
                vals[fname] = struct.unpack(">f", self.f.read(4))[0]
            elif ftype == "D":
                vals[fname] = struct.unpack(">d", self.f.read(8))[0]
            elif ftype in ("L", "["):
                vals[fname] = self.read_object()
            else:
                raise ValueError(f"Unknown field type: {ftype}")

        if cd["flags"] & self.SC_WRITE_METHOD:
            while True:
                pos = self.f.tell()
                ntc = self._u1()
                if ntc == self.TC_ENDBLOCKDATA:
                    break
                if ntc == self.TC_BLOCKDATA:
                    self.f.read(self._u1())
                elif ntc == self.TC_BLOCKDATALONG:
                    self.f.read(self._i4())
                else:
                    self.f.seek(pos)
                    self.read_object()
        return vals

    def read_object(self) -> object:
        tc = self._u1()
        if tc == self.TC_NULL:
            return None
        if tc == self.TC_REFERENCE:
            return self.handles[self._i4() - self.BASE_WIRE_HANDLE]
        if tc == self.TC_STRING:
            s = self._utf()
            self._register(s)
            return s
        if tc == self.TC_LONGSTRING:
            s = self._long_utf()
            self._register(s)
            return s
        if tc == self.TC_OBJECT:
            cd = self._read_classdesc()
            assert cd is not None
            idx = self._register({})
            obj: dict = {"_class": cd["name"]}
            obj.update(self._read_fields(cd))
            self.handles[idx] = obj
            return obj
        raise ValueError(f"Unhandled object token {tc:#x} at {self.f.tell()}")


def extract_installer(jar_path: str, dest_dir: str) -> None:
    packs = ("packs/pack-Core Windows/Linux", "packs/pack-French")
    os.makedirs(dest_dir, exist_ok=True)
    dest_real = os.path.realpath(dest_dir)

    with zipfile.ZipFile(jar_path, "r") as zf:
        for pack_name in packs:
            stream = JavaObjectStream(zf.read(pack_name))
            file_count = stream.read_block_int()
            for _ in range(file_count):
                pf = stream.read_object()
                if not isinstance(pf, dict):
                    raise ValueError(f"Expected PackFile dict, got {type(pf)}")
                if pf.get("pack200Jar"):
                    raise ValueError(f"Unsupported pack200 entry: {pf.get('targetPath')}")

                target = str(pf["targetPath"])
                is_dir = bool(pf["isDirectory"])
                length = int(pf["length"])
                data = b"" if is_dir else stream.read_block_bytes(length)

                rel = (
                    target.replace("$INSTALL_PATH/", "")
                    .replace("$INSTALL_PATH", "")
                    .replace("${langdir}/", "lib/langs/")
                    .lstrip("/")
                )
                if not rel:
                    continue

                out_path = os.path.realpath(os.path.join(dest_real, rel))
                if not (out_path == dest_real or out_path.startswith(dest_real + os.sep)):
                    raise ValueError(f"Path traversal detected: {target}")

                if is_dir:
                    os.makedirs(out_path, exist_ok=True)
                else:
                    os.makedirs(os.path.dirname(out_path), exist_ok=True)
                    with open(out_path, "wb") as out_f:
                        out_f.write(data)


def main() -> int:
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <installer.jar> <dest_dir>", file=sys.stderr)
        return 1
    extract_installer(sys.argv[1], sys.argv[2])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
