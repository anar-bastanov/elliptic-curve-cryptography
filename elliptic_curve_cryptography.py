
class ECPoint:
    def __init__(self, x: int = 0, y: int = 0):
        self.x = x
        self.y = y

    def __eq__(self, other) -> bool:
        return self.x == other.x and self.y == other.y

    def __str__(self) -> str:
        return f"({self.x}, {self.y})"

    def __repr__(self) -> str:
        return f"ECPoint({self.x}, {self.y})"


class Generator:
    def __init__(self, a: int, b: int, p: int, g: ECPoint):
        self.a = a
        self.b = b
        self.p = p
        self.points = [g]

        point = g
        while point:
            point = self.add_ecpoint(point, g)
            self.points.append(point)

        self.n = len(self.points)

    def add_ecpoint(self, lhs: ECPoint, rhs: ECPoint):
        if not lhs or not rhs:
            return None

        if lhs == rhs:
            if lhs.x == 0:
                return None
            s = ((3 * lhs.x * lhs.x + self.a) * pow(2 * lhs.y, -1, self.p)) % self.p
            x = (s * s - 2 * lhs.x) % self.p
            y = (s * (lhs.x - x) - lhs.y) % self.p
        else:
            if lhs.x == rhs.x:
                return None
            s = ((lhs.y - rhs.y) * pow(lhs.x - rhs.x, -1, self.p)) % self.p
            x = (s * s - (lhs.x + rhs.x)) % self.p
            y = (s * (lhs.x - x) - lhs.y) % self.p

        return ECPoint(x, y)

    def mul_ecpoint(self, lhs: ECPoint, rhs: int):
        result = lhs
        for _ in range(1, rhs):
            result = self.add_ecpoint(result, lhs)
        return result

    def __str__(self) -> str:
        return ", ".join(str(point) for point in self.points)

    def __repr__(self) -> str:
        return f"Generator(...)"


class Agent:
    def __init__(self, name: str):
        self.name = name
        self.knowledge = {}

    def add_information(self, tag: str, data) -> None:
        self.knowledge[tag] = data


class UnsecureChannel:
    def __init__(self):
        self.listeners = [Agent("Trudy")]

    def add_listener(self, listener: Agent) -> None:
        self.listeners.append(listener)

    def broadcast(self, tag: str, data) -> None:
        for listener in self.listeners:
            listener.add_information(tag, data)

    def dump(self):
        print('-' * 100)
        for agent in self.listeners:
            print(f"{agent.name + ':':10}", agent.knowledge)
        print('-' * 100)


def main():
    channel = UnsecureChannel()

    alice, bob = Agent("Alice"), Agent("Bob")

    channel.add_listener(alice)
    channel.add_listener(bob)

    channel.dump()

    a, b, p, g = 2, 2, 17, ECPoint(5, 1)
    channel.broadcast("a", a)
    channel.broadcast("b", b)
    channel.broadcast("p", p)
    channel.broadcast("g", g)

    channel.dump()

    generator = Generator(a, b, p, g)
    channel.broadcast("G", generator)

    print(generator)

    alpha = 9  # random.randint(1, generator.n)
    alice.add_information("alpha", alpha)

    beta = 3  # random.randint(1, generator.n)
    bob.add_information("beta", beta)

    channel.dump()

    A = generator.mul_ecpoint(g, alpha)
    channel.broadcast("A", A)

    B = generator.mul_ecpoint(g, beta)
    channel.broadcast("B", B)

    channel.dump()

    alice.add_information("AB", generator.mul_ecpoint(B, alpha))
    bob.add_information("AB", generator.mul_ecpoint(A, beta))

    channel.dump()


if __name__ == '__main__':
    main()
