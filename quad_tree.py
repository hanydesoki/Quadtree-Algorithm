import pygame

from typing import Any, Generator


class QuadTree:

    def __init__(self, x: float, y: float, w: float, h: float, capacity: int = 4, min_size: float = 10) -> None:
        self.x = x
        self.y = y
        self.w = w
        self.h = h

        self.rect = pygame.Rect(x, y, w, h)

        self.capacity = capacity
        self.min_size = min_size

        self.divided: bool = False

        self.ne: "QuadTree" | None = None
        self.nw: "QuadTree" | None = None
        self.se: "QuadTree" | None = None
        self.sw: "QuadTree" | None = None

        self._elements: set[Any] = set()

    def subdivide(self) -> None:

        w = self.w / 2
        h = self.h / 2

        if min(w, h) < self.min_size: return

        self.nw = QuadTree(
            x=self.x,
            y=self.y,
            w=w,
            h=h,
            capacity=self.capacity,
            min_size=self.min_size
        )

        self.ne = QuadTree(
            x=self.x + w,
            y=self.y,
            w=w,
            h=h,
            capacity=self.capacity,
            min_size=self.min_size
        )

        self.sw = QuadTree(
            x=self.x,
            y=self.y + h,
            w=w,
            h=h,
            capacity=self.capacity,
            min_size=self.min_size
        )

        self.se = QuadTree(
            x=self.x + w,
            y=self.y + h,
            w=w,
            h=h,
            capacity=self.capacity,
            min_size=self.min_size
        )

        for qt in self:
            for (e, ex, ey) in self._elements:
                qt.insert(e, ex, ey)
                
        self._elements.clear()

        self.divided = True

    def insert(self, element: Any, x: float, y: float) -> None:
        if not self.rect.collidepoint((x, y)): return

        if not self.divided:
            self._elements.add((element, x, y))

        if not self.divided and (len(self._elements) >= self.capacity):
            self.subdivide()
        elif self.divided:
            for qt in self:
                qt.insert(element, x, y)

    def all_leafs(self) -> Generator["QuadTree", None, None]:
        stack: list["QuadTree"] = [self]

        while stack:
            qtree = stack.pop()
            
            if qtree.divided:
                stack.extend(qtree)
            else:
                yield qtree

    def query_leafs(self, x: float, y: float, w: float, h: float) -> list["QuadTree"]:

        rect = pygame.Rect(x, y, w, h)
        
        stack: list["QuadTree"] = [self]

        all_leafs: list["QuadTree"] = []

        while stack:
            qtree = stack.pop()

            if not qtree.rect.colliderect(rect):
                continue
            
            if qtree.divided:
                stack.extend(qt for qt in qtree if qt.rect.colliderect(rect))
            else:
                all_leafs.append(qtree)
        
        return all_leafs
    
    def query_elements(self, x: float, y: float, w: float, h: float) -> list[Any]:
        all_elements: list[Any] = []
        rect = pygame.Rect(x, y, w, h)
        for (element, x_pos, y_pos) in set.union(*(qt._elements for qt in self.query_leafs(x, y, w, h))):
            if rect.collidepoint((x_pos, y_pos)):
                all_elements.append(element)

        return all_elements

    def __iter__(self) -> Generator["QuadTree", None, None]:
        yield self.nw
        yield self.ne
        yield self.sw
        yield self.se
