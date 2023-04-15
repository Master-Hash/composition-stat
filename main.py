from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import date
from os import chdir, scandir, sep
from os.path import exists, join, normpath, splitext
from re import MULTILINE
from typing import Literal
from urllib.parse import ParseResult, urlparse

ITEMDIR = [
    "人",
    "事",
    "物",
    "情思",
]

TITLE_REGEX = re.compile(r"^(.+)$\n={3,}$|^#\s(.+)$", MULTILINE)
FOOTNOTE_REGEX = re.compile(r"^\[\^\d+\]:\s(.+)$", MULTILINE)
ITEMTYPE_REGEX = re.compile(r"^type:\s(人|事|物|情思)$", MULTILINE)
DATE_REGEX = re.compile(r"^date:\s(\d{4}-\d{2}-\d{2})$", MULTILINE)
WIKILINK_REGEX = re.compile(
    r'^\[.+\]:\s(?!#)<?((?:\.\.\/(?:人|事|物|情思)\/)?(?:[^/\.]+?)(?:\.md)?)>?\s"(.+?)"$',
    MULTILINE,
)
# NOTE: see https://ihateregex.io/expr/url/ and slightly modified
# NOTE: https://jasontucker.blog/8945/what-is-the-longest-tld-you-can-get-for-a-domain-name
# FIXME: the closing parenthesis in Markdown syntax shouldn't become a part of the URL
URL_REGEX = re.compile(
    r"https?:\/\/[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9]{2,24}\b\/[-a-zA-Z0-9()!@:%_\+.~#?&\/=]*"
)


@dataclass
class Composition:
    data: str
    item_type: Literal["人", "事", "物", "情思"]
    title: str
    # NOTE: Only 事 has date.
    # The standard practice is to inherit Composition to represent different
    # types of compositions, and add a date field for 事, but I'm too lazy.
    # So no overload here. Keep in mind!
    date: date | None

    def __post_init__(self):
        if self.item_type == "事" and not self.date:
            raise ValueError("date is required for item_type 事")
        if self.item_type != "事" and self.date:
            raise ValueError("date is not allowed for item_type 人, 物, 情思")

    @property
    def path(self) -> str:
        return f"{self.date.isoformat() + '_' if self.date else ''}{self.item_type}{sep}{self.title}.md"

    footnotes: list[Footnote] = field(default_factory=list)
    wiki_link: list[WikiLink] = field(default_factory=list)

    @classmethod
    def from_file(cls, path: str) -> Composition:
        for composition in compositions:
            if composition.path == path:
                return composition

        with open(path, "r") as f:
            # print(path)
            data = f.read()
        _title = TITLE_REGEX.search(data)
        _item_type = ITEMTYPE_REGEX.search(data)
        _date = DATE_REGEX.search(data)
        _date1 = date.fromisoformat(_date[1]) if _date else None
        title = _title and (_title[1] or _title[2]) or ""
        item_type = _item_type[1] if _item_type else ""

        if not title or not item_type:
            raise ValueError(f"Title or item_type not found in {path}")

        # HACK: we have to do this because Python poorly supports
        # Literal type.
        if (
            item_type == "人"
            or item_type == "事"
            or item_type == "物"
            or item_type == "情思"
        ):
            _c = cls(data=data, item_type=item_type, title=title, date=_date1)
        else:
            raise ValueError(f"invalid item_type")
        compositions.append(_c)

        _footnotes = FOOTNOTE_REGEX.findall(data)
        for i in _footnotes:
            _c.footnotes.append(Footnote.from_data(i, _c))

        # TODO to make this work, we must get the file path
        # and create it recursively in advance.
        _wiki_links = WIKILINK_REGEX.findall(data)
        for _to_path, _ in _wiki_links:
            _c.wiki_link.append(WikiLink.from_data(_to_path, _c))

        return _c


@dataclass
class Footnote:
    # We have no order due to the design of Markdown.
    data: str
    url: ParseResult | None
    item_from: Composition

    @classmethod
    def from_data(cls, data: str, item_from: Composition) -> Footnote:
        """
        >>> Footnote.from_data("https://zh.moegirl.org.cn/%E9%87%8E%E5%85%BD%E5%85%88%E8%BE%88")
        Footnote(data='https://zh.moegirl.org.cn/%E9%87%8E%E5%85%BD%E5%85%88%E8%BE%88', url=ParseResult(scheme='https', netloc='zh.moegirl.org.cn', path='/%E9%87%8E%E5%85%BD%E5%85%88%E8%BE%88', params='', query='', fragment=''))

        >>> Footnote.from_data("OneNote")
        Footnote(data='OneNote', url=None)
        """

        # HACK: urlparse doesn't raise an error if the URL is invalid.
        # So we have to check it manually.
        if not URL_REGEX.match(data):
            _c = cls(data, None, item_from)
        else:
            _url = urlparse(data)
            url = _url if _url.scheme else None
            _c = cls(data, url, item_from)
        footnotes.append(_c)
        return _c


@dataclass
class WikiLink:
    item_from: Composition
    # Temporarily Optional because of many compositions written
    # but not committed yet.
    # TODO: make it compulsory.
    item_to: Composition | None = None

    @classmethod
    def from_data(cls, to_path: str, item_from: Composition) -> WikiLink:
        _p = normpath(join(item_from.path, "..", to_path))
        if splitext(_p)[1] != ".md":
            _p += ".md"
        if exists(_p):
            _item_to = Composition.from_file(_p)
            _c = cls(item_from, _item_to)
        else:
            _c = cls(item_from)
        item_link.append(_c)
        return _c


compositions: list[Composition] = []
footnotes: list[Footnote] = []
item_link: list[WikiLink] = []


def graph_walk(curdir: str = f"post-test{sep}情思"):
    ...


def main():
    chdir("post-test")
    for i in (f"{i}" for i in ITEMDIR):
        for item in scandir(i):
            if item.is_file():
                # TODO Decide if we have created it.
                Composition.from_file(item.path)
    print(compositions)


if __name__ == "__main__":
    main()
    print()
