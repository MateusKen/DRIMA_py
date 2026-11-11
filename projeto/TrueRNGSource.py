# projeto/TrueRNGSource.py
"""
Camada de acesso ao gerador de numeros verdadeiramente aleatorios (TrueRNG)
da familia ubld.it (documentacao em https://TrueRNG.net).
"""

import random as _pyrandom
import threading
import time

try:
    import serial
    from serial.tools import list_ports
    _PYSERIAL_DISPONIVEL = True
except ImportError:
    _PYSERIAL_DISPONIVEL = False


VID_PID_CONHECIDOS = [
    "04D8:F5FE",
    "04D8:EBB5",
    "16D0:0AA0",
]

BAUDRATE_PADRAO = 300
TIMEOUT_PADRAO_S = 5


class TrueRNGError(Exception):
    pass


class TrueRNGSource:

    def __init__(self, port: str = None):
        if not _PYSERIAL_DISPONIVEL:
            raise TrueRNGError(
                "A biblioteca 'pyserial' nao esta instalada. "
                "Instale com 'pip install pyserial' para usar o TrueRNG."
            )
        self._port_name = port or self._detectar_porta()
        if self._port_name is None:
            raise TrueRNGError(
                "Nenhum dispositivo TrueRNG foi encontrado nas portas seriais. "
                "Verifique se ele esta conectado (ver documentacao em https://TrueRNG.net)."
            )
        self._lock = threading.Lock()
        self._serial = None
        self._conectar()

    @staticmethod
    def _detectar_porta():
        if not _PYSERIAL_DISPONIVEL:
            return None
        for porta in list_ports.comports():
            hwid = (porta.hwid or "").upper()
            for vid_pid in VID_PID_CONHECIDOS:
                if vid_pid in hwid:
                    return porta.device
        return None

    def _conectar(self):
        try:
            self._serial = serial.Serial()
            self._serial.port = self._port_name
            self._serial.baudrate = BAUDRATE_PADRAO
            self._serial.timeout = TIMEOUT_PADRAO_S
            self._serial.dsrdtr = False
            self._serial.rtscts = False

            self._serial.open()

            self._serial.dtr = True
            self._serial.rts = True

            time.sleep(0.2)
            self._serial.reset_input_buffer()

            teste = self._serial.read(1)
            if len(teste) == 0:
                self._serial.dtr = False
                time.sleep(0.1)
                self._serial.dtr = True
                time.sleep(0.2)
                self._serial.reset_input_buffer()
                teste = self._serial.read(1)
                if len(teste) == 0:
                    self._serial.close()
                    raise TrueRNGError(
                        f"Conectou na porta {self._port_name}, mas nenhum byte foi recebido do "
                        "TrueRNG. Verifique se: (1) nenhum outro programa está com a porta aberta "
                        "(ex.: outro terminal, RNGTest, monitor serial); (2) o driver do dispositivo "
                        "está instalado corretamente (ver Gerenciador de Dispositivos / Device Manager); "
                        "(3) o cabo/porta USB está OK. Documentação: https://TrueRNG.net"
                    )
        except serial.SerialException as e:
            raise TrueRNGError(f"Falha ao abrir a porta serial do TrueRNG ({self._port_name}): {e}")

    def close(self):
        with self._lock:
            if self._serial is not None and self._serial.is_open:
                self._serial.close()

    def _ler_bytes(self, n: int) -> bytes:
        with self._lock:
            if self._serial is None or not self._serial.is_open:
                self._conectar()
            dados = self._serial.read(n)
        if len(dados) < n:
            raise TrueRNGError(
                f"Leitura incompleta do TrueRNG: esperava {n} bytes, recebeu {len(dados)}. "
                "Verifique a conexao do dispositivo."
            )
        return dados

    def random(self) -> float:
        """Float uniforme em [0.0, 1.0), usando 53 bits de entropia real do TrueRNG."""
        BPF = 53
        RECIP_BPF = 2 ** -BPF
        dados = self._ler_bytes(7)
        inteiro = int.from_bytes(dados, "big") >> 3
        return inteiro * RECIP_BPF

    def uniform(self, a: float, b: float) -> float:
        return a + (b - a) * self.random()

    def randint(self, a: int, b: int) -> int:
        """Inteiro aleatorio em [a, b], inclusive, via amostragem por rejeicao."""
        if a > b:
            a, b = b, a
        intervalo = b - a + 1
        n_bytes = max(1, (intervalo.bit_length() + 7) // 8)
        espaco_total = 1 << (n_bytes * 8)
        limite = espaco_total - (espaco_total % intervalo)
        while True:
            valor = int.from_bytes(self._ler_bytes(n_bytes), "big")
            if valor < limite:
                return a + (valor % intervalo)

    def choice(self, sequencia):
        if not sequencia:
            raise IndexError("Nao e possivel escolher de uma sequencia vazia.")
        indice = self.randint(0, len(sequencia) - 1)
        return sequencia[indice]

    def choices(self, populacao, weights=None, k=1):
        populacao = list(populacao)
        n = len(populacao)
        if weights is None:
            weights = [1.0] * n
        total = sum(weights)

        cumulativos = []
        acumulado = 0.0
        for w in weights:
            acumulado += w
            cumulativos.append(acumulado)

        resultado = []
        for _ in range(k):
            alvo = self.random() * total
            for i, limite in enumerate(cumulativos):
                if alvo <= limite:
                    resultado.append(populacao[i])
                    break
            else:
                resultado.append(populacao[-1])
        return resultado

    def sample(self, populacao, k):
        disponiveis = list(populacao)
        if k > len(disponiveis):
            raise ValueError("A amostra nao pode ser maior que a populacao.")
        resultado = []
        for _ in range(k):
            idx = self.randint(0, len(disponiveis) - 1)
            resultado.append(disponiveis.pop(idx))
        return resultado


_instancia = None
_habilitado = False


def set_enabled(habilitar: bool):

    global _instancia, _habilitado

    if not habilitar:
        if _instancia is not None:
            _instancia.close()
            _instancia = None
        _habilitado = False
        return True, "TrueRNG desabilitado. Usando gerador pseudo-aleatorio padrao."

    try:
        if _instancia is None:
            _instancia = TrueRNGSource()
        _habilitado = True
        return True, f"TrueRNG conectado na porta {_instancia._port_name}. Usando hardware para aleatoriedade."
    except TrueRNGError as e:
        _instancia = None
        _habilitado = False
        return False, str(e)


def is_enabled() -> bool:
    return _habilitado and _instancia is not None


def get_generator():

    if is_enabled():
        return _instancia
    return _pyrandom
