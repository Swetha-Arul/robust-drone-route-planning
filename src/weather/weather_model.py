import random
import math


class WeatherModel:

    def __init__(self):

        self.zones = []

    def generate_weather(self, x_size, y_size):

        self.zones.clear()

        # Rain zones
        for _ in range(2):
            self.zones.append((
                random.randint(4, x_size-4),
                random.randint(4, y_size-4),
                random.randint(3,4),
                "rain"
            ))

        # Wind zones
        for _ in range(2):
            self.zones.append((
                random.randint(4, x_size-4),
                random.randint(4, y_size-4),
                random.randint(3,4),
                "wind"
            ))

        # Storm zone
        self.zones.append((
            random.randint(5, x_size-5),
            random.randint(5, y_size-5),
            random.randint(4,5),
            "storm"
        ))

    def cost(self, pos):

        x, y, z = pos
        penalty = 0

        for cx, cy, radius, typ in self.zones:

            dist = math.sqrt((x-cx)**2 + (y-cy)**2)

            if dist < radius:

                if typ == "rain":
                    penalty += 2

                elif typ == "wind":
                    penalty += 4

                elif typ == "storm":
                    penalty += 8

        return penalty