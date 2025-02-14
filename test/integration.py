import os
import glob
import json

import libzim.reader
from warcio import ArchiveIterator


def get_zim_article(zimfile, path):
    zim_fh = libzim.reader.Archive(zimfile)
    return zim_fh.get_entry_by_path(path).get_item().content.tobytes()


def test_is_file():
    """Ensure ZIM file exists"""
    assert os.path.isfile("/output/isago.zim")


def test_zim_main_page():
    """Main page specified, http://isago.rskg.org/, was a redirect to https
    Ensure main page is the redirected page"""

    assert b'"https://isago.rskg.org/"' in get_zim_article(
        "/output/isago.zim", "A/index.html"
    )


def test_user_agent():
    """Test that mobile user agent was used in WARC request records with custom Zimit and email suffix"""

    found = False
    for warc in glob.glob("/output/.tmp*/collections/crawl-*/archive/*.warc.gz"):
        with open(warc, "rb") as fh:
            for record in ArchiveIterator(fh):
                if record.rec_type == "request":
                    print(record.http_headers)
                    ua = record.http_headers.get_header("User-Agent")
                    if ua:
                        assert "Pixel" in ua
                        assert ua.endswith(" +Zimit test@example.com")
                        found = True

    # should find at least one
    assert found


def test_stats_output():
    with open("/output/crawl.json") as fh:
        assert json.loads(fh.read()) == {
            "crawled": 5,
            "pending": 0,
            "pendingPages": [],
            "total": 5,
            "failed": 0,
            "limit": {"max": 0, "hit": False},
        }
    with open("/output/warc2zim.json") as fh:
        assert json.loads(fh.read()) == {
            "written": 9,
            "total": 9,
        }
    with open("/output/stats.json") as fh:
        assert json.loads(fh.read()) == {
            "done": 9,
            "total": 9,
            "limit": {"max": 0, "hit": False},
        }
