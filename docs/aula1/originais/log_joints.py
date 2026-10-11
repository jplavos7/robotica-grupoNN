import time
import matplotlib.pyplot as plt
from xarm.wrapper import XArmAPI

arm = XArmAPI('192.168.1.176', is_radian=False)
tempos = []
angulos = []
inicio = time.perf_counter()

while time.perf_counter() - inicio < 30:
    codigo, valores = arm.get_servo_angle()
    if codigo == 0:
        tempos.append(time.perf_counter() - inicio)
        angulos.append(valores[:6])

print('Amostras:', len(tempos))
print('Frequência média:', round((len(tempos)-1) / (tempos[-1]-tempos[0]), 1), 'Hz')

for junta in range(6):
    plt.plot(tempos, [a[junta] for a in angulos], label=f'J{junta+1}')

plt.xlabel('Tempo (s)')
plt.ylabel('Ângulo (graus)')
plt.legend()
plt.show()