# composition-stat

Les statistiques de mes compositions.

## 目标

### 提交历史

* 每篇文章的提交次数，每次提交的字数
* 提交频率
* 提交类型（feat/fix）

一定有误差，因为某些不规范的更名操作。

### 尾注

* 几成尾注单纯由 URL 组成？
  * 集中规律：除了 Wikipedia、萌娘百科和知乎，我还引用谁最多？
  * 我有没有必要添加更多标题、作者信息，以便顾名思义？
  * 复用：哪些 URL 我一再提及？我有没有必要建立复用系统（比方为之创建主条目）？
<!-- 个人感觉，能复用的作者更多于文章。 -->
* 几成尾注来自 OneNote？
* 几成尾注不可参考？

有些不属于统计范畴。比方能否一眼认出尾注是理论参考还是事实出处。

### 超链接

* 数量有限，可以提取出来目力研究

### 交叉引用

* 有多少我写好却没交的文章？

### dump

考虑我不需要在这里压 Markdown，似乎这里小改下就能担当 dump 的重任？

~~Deno 历史使命减减~~

## 语言选择

JavaScript 有诱人的 URL global、Promise API 和正则字面量，Python 虽然也有 urllib.parse、asyncio 和 re，但远远没那么顺手。

但 Python 有数据科学库。还有 @dataclass 和 @classmethod 这样的大杀器。（想起了 C++ 转 JavaScript 的 Xecades 最怀念的运算符重载）

假设我需要搞 `git log`，Python 还有一大好处：任务队列。JavaScript 奇缺高级数据结构标准库。（虽然我的任务量同步运行也慢不到哪里去）

## 数据结构

反正不可能用 JSON 类的结构。我给每类本体建了个 dataclass 列表，以模仿 SQL 的表。

如果要把对象关系当数据存起来，可以引用对象（我的方案；但就不能 dump 了），或者引用下标。

写入新条目会是个问题。我只能递归地把图一次画完，每次重画。（开个玩笑：假如难点在于无法比较更变，让 `git diff` 生成不就好了？嗯，假设哪天我想不开了，我会来试试。）

- [ ] 支持增量更新

```python
@dataclass
class Composition:
    data: str
    item_type: Literal["人", "事", "物", "情思"]
    title: str
    date: date | None

    @property
    def path(self) -> str: ...

    footnotes: list[Footnote] = field(default_factory=list)
    wiki_link: list[ItemLink] = field(default_factory=list)


@dataclass
class Footnote:
    data: str
    url: ParseResult | None
    item_from: Composition


@dataclass
class WikiLink:
    item_from: Composition
    item_to: Composition


"""
Valid WikiLink:
[家母]: 家母.md "家母"
[家母]: ../人/家母 "家母"
[家母]: ../人/家母.md "家母"
[家母#怀疑论者]: ../人/家母.md "家母"
[Word Power Made Easy]: <../物/Word Power Made Easy.md> "Word Power Made Easy"
The second example is valid but legacy.

Invaild WikiLink:
[ISSUE]: ../ISSUE "ISSUE"
[//end]: # "Autogenerated link references"
[//begin]: # "Autogenerated link references for markdown compatibility"

The first example is invalid because it doesn't have a correct type
and path depth.
"""
```
