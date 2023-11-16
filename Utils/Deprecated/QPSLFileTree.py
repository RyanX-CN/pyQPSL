from QPSLClass.Base import *
from Utils.UIClass.QPSLTreeView import QPSLTreeView


class QPSLFileTree(QPSLTreeView):

    def __init__(self,
                 parent: QWidget,
                 object_name: str,
                 dir_path: str,
                 header_label: str,
                 filter: Optional[Callable[[str], bool]] = None):
        super().__init__(parent, object_name)
        self.m_filter = filter
        self.setHeaderLabel(header_label)
        self.load_path(dir_path=dir_path)
        connect_direct(self.itemClicked, self.push_down)

    def load_path(self, dir_path: str):

        def dfs(path: str):
            path = os.path.abspath(path)
            if self.m_filter and (not self.m_filter(path)):
                return None
            item = QTreeWidgetItem()
            if not os.path.isfile(path):
                for sub in listdir(path):
                    res = dfs(sub)
                    if res:
                        item.addChild(res)
            item.setCheckState(0, 0)
            item.setText(0, os.path.basename(path))
            return item

        for f in listdir(dir_path=dir_path):
            res = dfs(f)
            if res:
                self.addTopLevelItem(res)

    def push_down(self, item: QTreeWidgetItem, column: int, push_up=True):
        state = item.checkState(column)

        def dfs(item: QTreeWidgetItem):
            for i in range(item.childCount()):
                dfs(item.child(i))
            item.setCheckState(column, state)

        dfs(item)
        if push_up:
            self.push_up(column=column)

    def push_up(self, column: int):

        def dfs(item: QTreeWidgetItem):
            hasBad, hasGood = False, False
            for i in range(item.childCount()):
                res = dfs(item.child(i))
                if res <= 1: hasBad = True
                if res >= 1: hasGood = True
            if hasBad:
                if hasGood: item.setCheckState(column, 1)
                else: item.setCheckState(column, 0)
            else:
                if hasGood: item.setCheckState(column, 2)
                else: pass
            return item.checkState(column)

        for i in range(self.topLevelItemCount()):
            dfs(self.topLevelItem(i))

    def to_dict(self, absolute: bool) -> Dict[str, Tuple[str, Dict]]:
        res = dict()

        def dfs(item: QTreeWidgetItem, cur: Dict):
            nxt = dict()
            if absolute:
                cur[os.path.abspath(item.text(0))] = (item.checkState(0), nxt)
            else:
                cur[item.text(0)] = (item.checkState(0), nxt)
            for i in range(item.childCount()):
                dfs(item.child(i), nxt)

        for i in range(self.topLevelItemCount()):
            dfs(item=self.topLevelItem(i), cur=res)
        return res

    def traverse_upward(self) -> Iterator[QTreeWidgetItem]:

        def dfs(item: QTreeWidgetItem):
            for i in range(item.childCount()):
                yield from dfs(item.child(i))
            yield item

        for i in range(self.topLevelItemCount()):
            yield from dfs(self.topLevelItem(i))

    def traverse_downward(self) -> Iterator[QTreeWidgetItem]:

        def dfs(item: QTreeWidgetItem):
            yield item
            for i in range(item.childCount()):
                yield from dfs(item.child(i))

        for i in range(self.topLevelItemCount()):
            yield from dfs(self.topLevelItem(i))