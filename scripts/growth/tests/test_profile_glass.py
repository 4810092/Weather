import unittest

from scripts.profile_glass import parse_frames, valid_frame


class GlassFrameEvidenceTest(unittest.TestCase):
    def test_both_android_headers_keep_column_identity_and_reset_boundary(self):
        for extra, value in (("", ""), ("FrameTimelineVsyncId,", "17,")):
            raw = (
                f"Flags,{extra}IntendedVsync,FrameDeadline,FrameCompleted,\n"
                f"0,{value}99,115,110,\n"
                f"0,{value}100,116,118,\n"
                f"0,{value}120,136,0,\n"
            )
            rows = list(parse_frames(raw, cutoff=100))
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["IntendedVsync"], 100)
            self.assertEqual(rows[0]["FrameDeadline"], 116)
            self.assertEqual(rows[0]["FrameCompleted"], 118)

    def test_flagged_and_nonpositive_frames_are_invalid_but_stalls_remain(self):
        self.assertFalse(valid_frame({"Flags": 8, "IntendedVsync": 100, "FrameCompleted": 120}))
        self.assertFalse(valid_frame({"Flags": 0, "IntendedVsync": 100, "FrameCompleted": 99}))
        self.assertFalse(valid_frame({"Flags": 0, "IntendedVsync": 100, "FrameCompleted": 100}))
        self.assertTrue(valid_frame({"Flags": 0, "IntendedVsync": 100, "FrameCompleted": 20_000_000_100}))

    def test_overlapping_rolling_samples_do_not_count_duplicate_frames(self):
        header = "Flags,IntendedVsync,FrameDeadline,FrameCompleted,\n"
        frames = {}
        for raw in (header + "0,100,116,110,\n", header + "0,100,116,110,\n0,120,136,140,\n"):
            for row in parse_frames(raw, cutoff=0):
                frames[row["IntendedVsync"]] = row
        self.assertEqual(len(frames), 2)
        self.assertEqual(sum(r["FrameCompleted"] > r["FrameDeadline"] for r in frames.values()), 1)
