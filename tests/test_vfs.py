"""Tests of the virtual file system model (loading, paths, motd)."""

import os
import tempfile
import unittest

from vfs import VFS, Directory, File, VFSError


class VFSFixture(unittest.TestCase):
    """Creates a temporary directory with a small tree on the disk."""

    def setUp(self):
        """Build a real tree: motd, a binary file and nested folders."""
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = os.path.join(self.tmp.name, "mydisk")
        os.makedirs(os.path.join(self.base, "a", "b", "c"))
        self.write("motd", b"hello\n")
        self.write("bin.dat", bytes(range(256)))
        self.write("a/b/c/deep.txt", b"deep")

    def write(self, relative, data):
        """Write bytes to a file inside the temporary tree."""
        with open(os.path.join(self.base, relative), "wb") as handle:
            handle.write(data)


class LoadTest(VFSFixture):
    """Loading from a directory on the disk."""

    def test_load_tree_and_binary(self):
        """Nested folders and binary data are loaded unchanged."""
        vfs = VFS.from_directory(self.base)
        self.assertEqual(vfs.name, "mydisk")
        self.assertEqual(vfs.get("/bin.dat").data, bytes(range(256)))
        self.assertEqual(vfs.get("/a/b/c/deep.txt").data, b"deep")

    def test_disk_is_not_modified(self):
        """Changing the VFS in memory does not touch the disk."""
        vfs = VFS.from_directory(self.base)
        del vfs.root.children["motd"]
        self.assertTrue(os.path.exists(os.path.join(self.base, "motd")))

    def test_missing_path(self):
        """A missing directory is reported."""
        with self.assertRaises(VFSError):
            VFS.from_directory(os.path.join(self.tmp.name, "nope"))

    def test_not_a_directory(self):
        """A regular file instead of a directory is an invalid format."""
        with self.assertRaises(VFSError):
            VFS.from_directory(os.path.join(self.base, "motd"))


class PathTest(unittest.TestCase):
    """Path normalization and lookup."""

    def setUp(self):
        """Create a tiny VFS /d/f."""
        root = Directory({"d": Directory({"f": File(b"x")})})
        self.vfs = VFS("t", root)

    def test_normalize(self):
        """Dots and double slashes are resolved, root is the limit."""
        self.assertEqual(self.vfs.normalize("/d/./x/../f"), ["d", "f"])
        self.assertEqual(self.vfs.normalize("/../.."), [])

    def test_relative_to_cwd(self):
        """Relative paths start from the current directory."""
        self.vfs.cwd = ["d"]
        self.assertEqual(self.vfs.normalize("f"), ["d", "f"])
        self.assertEqual(self.vfs.cwd_path(), "/d")

    def test_get_missing(self):
        """Looking up a missing node raises VFSError."""
        with self.assertRaises(VFSError):
            self.vfs.get("/d/zzz")
        with self.assertRaises(VFSError):
            self.vfs.get("/d/f/inside")


class MotdTest(VFSFixture):
    """The message of the day."""

    def test_motd(self):
        """motd in the root is returned without the trailing newline."""
        self.assertEqual(VFS.from_directory(self.base).motd(), "hello")

    def test_no_motd(self):
        """Without motd an empty string is returned."""
        self.assertEqual(VFS.default().motd(), "")


if __name__ == "__main__":
    unittest.main()
