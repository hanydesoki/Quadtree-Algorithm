class Circle:

    vector_force = [0, 0]
    collision_damping = 0.80

    def __init__(
            self, 
            x: float, 
            y: float, 
            radius: float, 
            vx: float = 0, 
            vy: float = 0,
            metadata: dict | None = None
    ) -> None:
        self.x = x
        self.y = y
        self.radius = radius
        self.vx = vx
        self.vy = vy

        self.metadata = {} if metadata is None else {}

    def squared_distance(self, point: tuple[float, float]) -> float:
        return pow(self.x - point[0], 2) + pow(self.y - point[1], 2)
    
    def collide_circle(self, other: "Circle") -> bool:
        return self.squared_distance(other.center) < pow(self.radius + other.radius, 2)

    def update(self, x: float, y: float, w: float, h: float) -> None:
        self.x += self.vx
        self.y += self.vy

        self.vx += self.vector_force[0]
        self.vy += self.vector_force[1]

        if self.x - self.radius < x:
            self.x = self.radius
            self.vx *= -1 * self.collision_damping
        elif self.x + self.radius > x + w:
            self.x = x + w - self.radius
            self.vx *= -1 * self.collision_damping

        if self.y - self.radius < y:
            self.y = self.radius
            self.vy *= -1 * self.collision_damping
        elif self.y + self.radius > y + h:
            self.y = y + h - self.radius
            self.vy *= -1 * self.collision_damping

    @property
    def center(self) -> tuple[float, float]:
        return self.x, self.y
    
    def __repr__(self):
        return f"Circle({self.x}, {self.y}, {self.radius}, {self.vx}, {self.vy})"