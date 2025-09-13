from __future__ import annotations

from typing import List
from unittest.mock import patch

from ..src.models import Filters, Paper
from ..src.tools.arxiv_tool import search_arxiv
from ..src.tools.pubmed_tool import search_pubmed
from ..src.tools.crossref_tool import search_crossref


def test_arxiv_tool_parses_entries():
    xml = """
    <feed xmlns="http://www.w3.org/2005/Atom">
      <entry>
        <id>http://arxiv.org/abs/1234.5678v1</id>
        <title>Test Paper</title>
        <summary>Abstract text.</summary>
        <author><name>Alice</name></author>
        <link rel="alternate" href="http://arxiv.org/abs/1234.5678v1"/>
        <link title="pdf" href="http://arxiv.org/pdf/1234.5678v1"/>
        <published>2023-01-01T00:00:00Z</published>
      </entry>
    </feed>
    """.strip()
    with patch("httpx.Client.get") as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.text = xml
        res = search_arxiv("test", Filters(limit=5))
        assert len(res) == 1
        p = res[0]
        assert isinstance(p, Paper)
        assert p.source == "arxiv"
        assert p.title == "Test Paper"
        assert p.year == 2023


def test_pubmed_tool_parses_summary():
    esearch_xml = """
    <eSearchResult><IdList><Id>111</Id></IdList></eSearchResult>
    """.strip()
    esummary_xml = """
    <eSummaryResult>
      <DocSum>
        <Id>111</Id>
        <Item Name="Title" Type="String">PM Title</Item>
        <Item Name="AuthorList" Type="List">
          <Item Name="Author" Type="String">Bob</Item>
        </Item>
        <Item Name="PubDate" Type="String">2022 Jan</Item>
        <Item Name="FullJournalName" Type="String">Journal</Item>
        <Item Name="ELocationID" Type="DOI">10.1000/xyz</Item>
      </DocSum>
    </eSummaryResult>
    """.strip()
    with patch("httpx.Client.get") as mock_get:
        mock_get.side_effect = [
            type("R", (), {"status_code": 200, "text": esearch_xml, "raise_for_status": lambda: None})(),
            type("R", (), {"status_code": 200, "text": esummary_xml, "raise_for_status": lambda: None})(),
        ]
        res = search_pubmed("test", Filters(limit=5))
        assert len(res) == 1
        p = res[0]
        assert p.source == "pubmed"
        assert p.title == "PM Title"
        assert p.venue == "Journal"
        assert p.doi == "10.1000/xyz"


def test_crossref_tool_parses_items():
    payload = {
        "message": {
            "items": [
                {
                    "title": ["CR Title"],
                    "issued": {"date-parts": [[2021]]},
                    "container-title": ["Conf"],
                    "author": [{"given": "C", "family": "D"}],
                    "DOI": "10.1000/abc",
                    "URL": "https://dx.doi.org/10.1000/abc",
                }
            ]
        }
    }
    with patch("httpx.Client.get") as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json = lambda: payload
        mock_get.return_value.raise_for_status = lambda: None
        res = search_crossref("test", Filters(limit=5))
        assert len(res) == 1
        p = res[0]
        assert p.source == "crossref"
        assert p.title == "CR Title"
        assert p.year == 2021
