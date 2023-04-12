from __future__ import annotations

from dataclasses import dataclass, field
from os import scandir, sep
from re import MULTILINE, compile
from urllib.parse import ParseResult, urlparse

ITEMDIR = [
    "人",
    "事",
    "物",
    "情思",
]

TITLE_REGEX = compile(r"^(.+)$\n={3,}$|^#\s(.+)$", MULTILINE)
FOOTNOTE_REGEX = compile(r"^\[\^\d+\]:\s(.+)$", MULTILINE)
ITEMTYPE_REGEX = compile(rf"^type:\s({'|'.join(ITEMDIR)})$", MULTILINE)
# TODO: get file path and filename \1 ref
ITEMLINK_REGEX = compile(r'^\[.+\]:\s(?!#).+?(?:.md)?\s"(.+?)"$', MULTILINE)


@dataclass
class Composition:
    data: str
    # item_type: Literal["人", "事", "物", "情思"]
    item_type: str
    title: str
    # TODO file path

    footnotes: list[Footnote] = field(default_factory=list)
    item_link: list[ItemLink] = field(default_factory=list)

    @classmethod
    def from_file(cls, path: str) -> Composition:
        with open(path, "r") as f:
            data = f.read()
        _title = TITLE_REGEX.search(data)
        title = _title and (_title[1] or _title[2]) or ""
        _item_type = ITEMTYPE_REGEX.search(data)
        item_type = _item_type[1] if _item_type else ""

        if not title or not item_type:
            raise ValueError(f"Title or item_type not found in {path}")

        _c = cls(data=data, item_type=item_type, title=title)

        _footnotes = FOOTNOTE_REGEX.findall(data)
        footnotes = [Footnote.from_data(i, _c) for i in _footnotes]
        _c.footnotes = footnotes

        # TODO to make this work, we must get the file path
        # and create it recursively in advance.

        _item_link = ITEMLINK_REGEX.findall(data)

        compositions.append(_c)
        return _c


@dataclass
class Footnote:
    # We have no order
    data: str
    url: ParseResult | None
    composition_from: Composition

    @classmethod
    def from_data(cls, data: str, composition_from: Composition) -> Footnote:
        """
        >>> Footnote.from_data("https://zh.moegirl.org.cn/%E9%87%8E%E5%85%BD%E5%85%88%E8%BE%88")
        Footnote(data='https://zh.moegirl.org.cn/%E9%87%8E%E5%85%BD%E5%85%88%E8%BE%88', url=ParseResult(scheme='https', netloc='zh.moegirl.org.cn', path='/%E9%87%8E%E5%85%BD%E5%85%88%E8%BE%88', params='', query='', fragment=''))

        >>> Footnote.from_data("OneNote")
        Footnote(data='OneNote', url=None)
        """
        _url = urlparse(data)
        url = _url if _url.scheme else None
        _c = cls(data, url, composition_from)
        footnotes.append(_c)
        return _c


@dataclass
class ItemLink:
    item_from: Composition
    item_to: Composition


compositions: list[Composition] = []
footnotes: list[Footnote] = []
item_link = []


def main():
    for i in (f"post-test{sep}{i}" for i in ITEMDIR):
        for item in scandir(i):
            if item.is_file():
                # TODO Decide if we have created it.
                Composition.from_file(item.path)
    print(compositions)


if __name__ == "__main__":
    main()
    print()
