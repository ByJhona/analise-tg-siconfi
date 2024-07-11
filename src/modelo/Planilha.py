from datetime import datetime  # Importa a classe datetime do módulo datetime para manipulação de datas
import pandas as pd  # Importa o pandas, uma biblioteca poderosa para manipulação de dados em Python
from pandas import DataFrame  # Importa especificamente a classe DataFrame do pandas
import locale  # Importa o módulo locale para configurações de localização (como formatos de data)
from typing import List, Tuple, Dict  # Importa ferramentas para tipagem do Python


# Define a localização para português do Brasil
locale.setlocale(locale.LC_ALL, "pt_BR.utf8")

class Planilha:
    """Classe para manipulação e análise de planilhas."""
    
    @classmethod
    def normalizar_planilhas(cls, planilhas_TG: List[DataFrame], planilhas_SICONFI: List[DataFrame]) -> Tuple[List[DataFrame], List[DataFrame]]:
        """Normaliza as planilhas."""
        # Cria dicionários para as planilhas TG e SICONFI
        dict_tg: Dict[str, DataFrame] = cls.criar_dicionario_planilhas(planilhas_TG)
        dict_siconfi: Dict[str, DataFrame] = cls.criar_dicionario_planilhas(planilhas_SICONFI)

        # Alinha e normaliza as planilhas
        lista_tg_normalizada, lista_siconfi_normalizada = cls.alinhar_e_normalizar_planilhas(dict_tg, dict_siconfi)
        return lista_tg_normalizada, lista_siconfi_normalizada

    @classmethod
    def alinhar_e_normalizar_planilhas(cls, dict_tg: Dict[str, DataFrame], dict_siconfi: Dict[str, DataFrame]) -> Tuple[List[DataFrame], List[DataFrame]]:
        lista_tg_normalizada: List[DataFrame] = []
        lista_siconfi_normalizada: List[DataFrame] = []

        # Para cada planilha SICONFI, alinha e normaliza com a respectiva planilha TG
        for siconfi, planilha_siconfi in dict_siconfi.items():
            planilha_tg: DataFrame = dict_tg.get(siconfi)
            left, right = cls.alinhar_planilhas(planilha_tg, planilha_siconfi)
            left, right = cls.normalizar_valores(left, right)
            left = cls.ordenar_colunas(left)
            right = cls.ordenar_colunas(right)
            left.Name, right.Name = siconfi, siconfi

            lista_siconfi_normalizada.append(right)
            lista_tg_normalizada.append(left)

        return lista_tg_normalizada, lista_siconfi_normalizada

    @staticmethod
    def alinhar_planilhas(planilha_tg: DataFrame, planilha_siconfi: DataFrame) -> Tuple[DataFrame, DataFrame]:
        # Alinha as planilhas TG e SICONFI pelas linhas e colunas
        right, left = planilha_siconfi.align(planilha_tg, join="outer", axis=0)
        right, left = right.align(left, join="outer", axis=1)
        return left, right

    @staticmethod
    def normalizar_valores(left: DataFrame, right: DataFrame) -> Tuple[DataFrame, DataFrame]:
        # Preenche valores nulos com zero
        left.fillna(0, inplace=True)
        right.fillna(0, inplace=True)
        return left, right

    @classmethod
    def ordenar_colunas(cls, planilha: DataFrame) -> DataFrame:
        # Ordena as colunas da planilha usando uma função de conversão para datetime
        colunas_reordenadas: List[str] = sorted(planilha.columns, key=cls.__convert_to_datetime)
        return planilha[colunas_reordenadas]

    @staticmethod
    def __convert_to_datetime(column_name: str) -> datetime:
        # Converte o nome da coluna para um objeto datetime, ou retorna uma data padrão se falhar
        try:
            return datetime.strptime(column_name, "%b/%Y")
        except ValueError:
            return datetime(9999, 12, 31)

    @classmethod
    def criar_dicionario_planilhas(cls, planilhas: List[DataFrame]) -> Dict[str, DataFrame]:
        """Cria um dicionário de planilhas a partir de uma lista de DataFrames."""
        return {planilha.Name: planilha for planilha in planilhas}

    @classmethod
    def subtrair_planilhas(cls, planilhas_tg: List[DataFrame], planilhas_siconfi: List[DataFrame]) -> List[DataFrame]:
        # Cria dicionários para as planilhas TG e SICONFI
        dict_tg: Dict[str, DataFrame] = cls.criar_dicionario_planilhas(planilhas_tg)
        dict_siconfi: Dict[str, DataFrame] = cls.criar_dicionario_planilhas(planilhas_siconfi)
        # Subtrai as planilhas SICONFI das planilhas TG
        return [cls.subtrair_diferenca(dict_tg[key], dict_siconfi[key]) for key in dict_tg]

    @staticmethod
    def subtrair_diferenca(tg: DataFrame, siconfi: DataFrame) -> DataFrame:
        # Subtrai os valores da planilha SICONFI dos valores da planilha TG
        diferenca: DataFrame = tg.sub(siconfi, axis=0, fill_value=0)
        diferenca = diferenca.map(lambda x: "R$ {:,.2f}".format(x))

        diferenca.Name = tg.Name
        return diferenca

    @classmethod
    def mesclar_planilhas(cls, planilhas_tg: List[DataFrame], planilhas_siconfi: List[DataFrame]) -> List[DataFrame]:
        # Cria dicionários para as planilhas TG e SICONFI
        dict_tg: Dict[str, DataFrame] = cls.criar_dicionario_planilhas(planilhas_tg)
        dict_siconfi: Dict[str, DataFrame] = cls.criar_dicionario_planilhas(planilhas_siconfi)
        # Mescla as planilhas TG e SICONFI
        return [cls.mesclar_parametros(dict_tg[key], dict_siconfi[key]) for key in dict_tg]

    @classmethod
    def mesclar_parametros(cls, tg: DataFrame, siconfi: DataFrame) -> DataFrame:
        planilha_comparada = tg.compare(siconfi, result_names=('TG', 'SICONFI'))
        planilha_comparada.Name = tg.Name
        return planilha_comparada

