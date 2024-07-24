import os
import smbus  # import SMBus module of I2C
from time import sleep  # import
import csv

class Acelerometro:
    BUS = smbus.SMBus(2)
    ENDERECO_ACELEROMETRO = 0x68
    CANAIS = [0b00000001, 0b00000010, 0b00000100, 0b00001000, 0b00010000, 0b00100000, 0b01000000, 0b10000000]
    PWR_MGMT_1 = 0x6B
    SMPLRT_DIV = 0x19
    CONFIG = 0x1A
    GYRO_CONFIG = 0x1B
    INT_ENABLE = 0x38
    ACCEL_XOUT_H = 0x3B
    ACCEL_YOUT_H = 0x3D
    ACCEL_ZOUT_H = 0x3F
    GYRO_XOUT_H = 0x43
    GYRO_YOUT_H = 0x45
    GYRO_ZOUT_H = 0x47

    def __init__(self, endereco_multiplexador):
        self.endereco_multiplexador = endereco_multiplexador
        self.canal = Acelerometro.CANAIS[0]

    @staticmethod
    def verifica_diretorio(input_str):
        """Faz a verificação de pastas já existentes, para não sobrescrever nenhum arquivo.
        :param input_str: Contém o caminho para o endereço e a pasta a ser criada
        :return: Retorna o nome definitivo para a pasta, a ser utilizado psoteriormente.
        """
        num = 1
        diretorio_atual = [input_str, num]
        while os.path.exists(f"{diretorio_atual[0]}{diretorio_atual[1]}"):
            num += 1
            diretorio_atual[1] = num

        nome_definitivo = str(f"{diretorio_atual[0]}{diretorio_atual[1]}")
        os.makedirs(nome_definitivo)
        return nome_definitivo

    def mpu_init(self):
        """Faz a configuração inicial dos bits do MPU6050"""
        # Escrever no registro de taxa de amostragem
        Acelerometro.BUS.write_byte_data(Acelerometro.ENDERECO_ACELEROMETRO, Acelerometro.SMPLRT_DIV, 7)

        # Escrever no registro de gerenciamento de energia
        Acelerometro.BUS.write_byte_data(Acelerometro.ENDERECO_ACELEROMETRO, Acelerometro.PWR_MGMT_1, 1)

        # Escrever no registro de configuração
        Acelerometro.BUS.write_byte_data(Acelerometro.ENDERECO_ACELEROMETRO, Acelerometro.CONFIG, 0x05)

        Acelerometro.BUS.write_byte_data(Acelerometro.ENDERECO_ACELEROMETRO, 0x1C, 0x10)  # Configurando acelerometro para 8g

        # Escrever no registro de configuração do giroscópio
        Acelerometro.BUS.write_byte_data(Acelerometro.ENDERECO_ACELEROMETRO, Acelerometro.GYRO_CONFIG, 0x08)

        # Escrever no registro de habilitação de interrupção
        Acelerometro.BUS.write_byte_data(Acelerometro.ENDERECO_ACELEROMETRO, Acelerometro.INT_ENABLE, 1)

    def ativa_canal(self):
        Acelerometro.BUS.write_byte(self.endereco_multiplexador, self.canal)

    def desativa_canais(self):
        Acelerometro.BUS.write_byte(self.endereco_multiplexador, 0x00)

    def read_raw_data(self, addr):
        self.ativa_canal()
        # Isso porque acelerômetro e giroscópio têm 16 bit, divide em parte baixa (8 bits menos significativos) e parte alta (8 bits mais significativos)
        high = Acelerometro.BUS.read_byte_data(Acelerometro.ENDERECO_ACELEROMETRO, addr)
        low = Acelerometro.BUS.read_byte_data(Acelerometro.ENDERECO_ACELEROMETRO, addr + 1)

        # Concatenar maior e menor valor
        value = ((high << 8) | low)

        # Para obter o valor assinado do MPU6050
        if (value > 32768):
            value = value - 65536
        self.desativa_canais()
        return value

    def rotaciona_canal(self):
        """"Realiza a rotação à esquerda dos bits de canal"""
        # match self.canal:
        #     case 0b00000001:
        #         return 0b00000010
        #     case 0b00000010:
        #         return 0b00000100
        #     case 0b00000100:
        #         return 0b00001000
        #     case 0b00001000:
        #         return 0b00010000
        #     case 0b00010000:
        #         return 0b00100000
        #     case 0b00100000:
        #         return 0b01000000
        #     case 0b01000000:
        #         return 0b10000000
        #     case 0b10000000:
        #         return 0b00000001
        #     case _:
        #         return 0b00000001
        if self.canal in Acelerometro.CANAIS:
            idx = Acelerometro.CANAIS.index(self.canal)
            self.canal = Acelerometro.CANAIS[(idx + 1) % len(Acelerometro.CANAIS)]
        else:
            self.canal = Acelerometro.CANAIS[0]


    def pegaAcelerometro(self, diretorio):
        """Método principal para o armazenamento dos dados do acelerômetro"""
        with open(f'{diretorio}/acelerometro.csv', mode='w', newline='') as csv_file:
            self.mpu_init()
            writer = csv.DictWriter(csv_file, fieldnames=['AccX0', 'AccY0', 'AccZ0', 'AccX1', 'AccY1', 'AccZ1', 'AccX2', 'AccY2',
                                                          'AccZ2', 'AccX3', 'AccY3', 'AccZ3', 'AccX4', 'AccY4', 'AccZ4', 'AccX5',
                                                          'AccY5', 'AccZ5', 'AccX6', 'AccY6', 'AccZ6', 'AccX7', 'AccY7', 'AccZ7'])
            writer.writeheader()

            while True:
                try:
                    self.ativa_canal()

                    # Lendo acelerometro
                    acc_x = self.read_raw_data(Acelerometro.ACCEL_XOUT_H)
                    acc_y = self.read_raw_data(Acelerometro.ACCEL_YOUT_H)
                    acc_z = self.read_raw_data(Acelerometro.ACCEL_ZOUT_H)

                    # Lendo giroscópio
                    # gyro_x = read_raw_data(GYRO_XOUT_H)
                    # gyro_y = read_raw_data(GYRO_YOUT_H)
                    # gyro_z = read_raw_data(GYRO_ZOUT_H)

                    # Convertendo as medidas para valores físicos
                    AccX = (acc_x / 4096)
                    AccY = (acc_y / 4096)
                    AccZ = (acc_z / 4096)

                    dados_float = list(map(float, [AccX, AccY, AccZ]))

                    testa_index = Acelerometro.CANAIS.index(self.canal)

                    dados_zipados = dict(zip([f'AccX{testa_index}', f'AccY{testa_index}', f'AccZ{testa_index}'], dados_float))
                    writer.writerow(dados_zipados)
                    print(dados_float)
                    csv_file.flush()
                    self.rotaciona_canal()

                except:
                    dados_float = [0, 0, 0]
                    dados_zipados = dict(zip([f'AccX{testa_index}', f'AccY{testa_index}', f'AccZ{testa_index}'], dados_float))
                    writer.writerow(dados_zipados)
                    print(dados_float)
                    csv_file.flush()
                    self.rotaciona_canal()
                sleep(0.1)