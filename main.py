import threading
from acelerometro import verifica_diretorio, Acelerometro

diretorio = verifica_diretorio('Logs/Rep')

Multiplexador1 = Acelerometro(0x70)

# Ajuste os threadings de acordo com a classe
t1 = threading.Thread(target=Multiplexador1.pegaAcelerometro, args=(diretorio,))

t1.start()

t1.join()
