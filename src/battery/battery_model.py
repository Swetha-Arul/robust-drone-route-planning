from typing import Tuple

Position = Tuple[int, int, int]

class BatteryModel:
    def __init__(self, base_cost_per_unit=1.0):
        self.base_cost_per_unit = base_cost_per_unit

    def step_cost(self, a, b, payload_weight, weather=None):

        dx = abs(a[0] - b[0])
        dy = abs(a[1] - b[1])
        dz = abs(a[2] - b[2])

        distance = (dx*dx + dy*dy + dz*dz) ** 0.5

        payload_factor = 1 + (payload_weight * 0.4)

        if dz > 0:
            altitude_factor = 2.5
        elif dz < 0:
            altitude_factor = 0.8
        else:
            altitude_factor = 1.0

        weather_factor = 1.0
        if weather:
            weather_factor += weather.cost(b) * 0.1

        return distance * payload_factor * altitude_factor * weather_factor