import machine


class PWM(machine.PWM):
    def _init(self, min=0, max=100):
        self._min = min * 655.35
        self._max = max * 655.35
        return self

    def duty_100(self, n=None):
        if n is None:
            return self.duty_u16() / 655.35

        n *= 655.35
        n = round(n)

        if n > self._max:
            n = 65535
        elif n < self._min:
            n = 0

        self.duty_u16(n)
