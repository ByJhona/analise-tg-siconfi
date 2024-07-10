from datetime import datetime
from math import floor
import pandas as pd
from pandas import DataFrame
import locale
import re
from typing import List, Dict, Union
# Configuração do local para o Brasil
locale.setlocale(locale.LC_ALL, "pt_BR.utf8")

class PlanilhaTG:
    
    def __init__(self, caminho_planilhas: str):
        # Inicialização das variáveis
        self.planilhas_TG: List[DataFrame] = []
        self.planilhas_TG_NAO_FORMATADAS: Dict[str, DataFrame] = {}
        self.exercicio: Union[int, None] = None
        self.periodo: Union[int, None] = None
        self.periodicidade: str = "Q"
        self.cod_ibge: str = "1"
        self.uf: str = "BR"
        self.co_poder: str = "J"
        self.co_tipo_demonstrativo: str = "RGF"
        self.anexo: str = "RGF-Anexo 01"
        self.esfera: str = "U"
        self.rotulo: str = "Padrão"
        
        # Métodos de inicialização das planilhas
        self.__abrir_planilhas(caminho_planilhas)
        self.__processar_planilhas()

    def __definir_planilha(self, planilha_df: DataFrame, pasta_trabalho: str) -> DataFrame:
        # Define a planilha com base no DataFrame fornecido
        cabecalho: str = "Mês Lançamento"
        colunas_ref: List[str] = ["Indices", "Mês 1", "Mês 2", "Mês 3", "Mês 4", "Mês 5", "Mês 6", "Mês 7", "Mês 8","Mês 9","Mês 10","Mês 11","Mês 12","RPNP"]
        # Cria um DataFrame vazio com as colunas definidas em 'colunas_ref'
        planilha: DataFrame = pd.DataFrame(columns=colunas_ref)

        for index, linha in planilha_df.iterrows():
            if linha.iloc[0] == cabecalho:

                # Preenche o DataFrame 'planilha' com linhas definidas pela função '__definir_linhas_planilha',
                # passando 'planilha', 'planilha_df' e 'index' como argumentos
                planilha = self.__definir_linhas_planilha(planilha, planilha_df, index)

                # Obtém uma lista das colunas do DataFrame 'planilha_df' na linha especificada por 'index'
                colunas_df: List[str] = planilha_df.loc[index].tolist()

                # Atualiza o DataFrame 'planilha' com as colunas obtidas em 'colunas_df'
                planilha = self.__atualizar_colunas_planilha(planilha, colunas_df)

                # Define a coluna 'cabecalho' como índice do DataFrame 'planilha' e remove o nome do índice
                planilha.set_index(cabecalho, inplace=True)
                planilha.index.name = None

                # Converte todos os dados do DataFrame 'planilha' para valores numéricos, substituindo erros por NaN
                planilha = planilha.apply(pd.to_numeric, errors="coerce")

                # Substitui todos os valores NaN por 0 no DataFrame 'planilha'
                planilha.fillna(0, inplace=True)

                # Define uma coluna total no DataFrame 'planilha' utilizando a função '__definir_coluna_total'
                planilha = self.__definir_coluna_total(planilha)

                # Define o nome do tribunal no DataFrame 'planilha' utilizando a função '__definir_nome_tribunal'
                # e o nome da pasta de trabalho 'pasta_trabalho'
                planilha = self.__definir_nome_tribunal(planilha, pasta_trabalho)

                # Define o ano e o quadrimestre no DataFrame 'planilha' utilizando a função '__set__ano_quadrimestre'
                self.__set__ano_quadrimestre(planilha)

                # Retorna o DataFrame 'planilha' após todas as modificações
                return planilha

    def __definir_linhas_planilha(self, planilha: DataFrame, planilha_df: DataFrame, index: int) -> DataFrame:
        # Define as linhas da planilha a partir do DataFrame fornecido
        tamanho_df: int = planilha_df.index.size
        quant_colunas: int = len(planilha.columns)
        for i in range(index + 1, tamanho_df):
            linha: List[Union[int, float, str]] = planilha_df.iloc[i].tolist()
            if len(linha) < quant_colunas:
                linha.append(0)
            planilha.loc[len(planilha)] = linha
        return planilha

    def __atualizar_colunas_planilha(self, planilha: DataFrame, colunas_df: List[str]) -> DataFrame:
        # Atualiza as colunas da planilha
        coluna_despesa: str = planilha.columns[-1]
        if len(colunas_df) < len(planilha.columns):
            colunas_df.append(coluna_despesa)
        else:
            colunas_df[-1] = coluna_despesa
        planilha.columns = colunas_df
        return planilha

    def __definir_coluna_total(self, planilha: DataFrame) -> DataFrame:
        # Define a coluna de total na planilha
        tamanho: int = planilha.index.size
        totais: List[float] = []
        for linha in range(tamanho):
            total: float = sum(planilha.iloc[linha, :12])
            totais.append(round(total, 2))
        planilha.insert(len(planilha.columns), "TOTAL", totais)
        return planilha

    def __definir_nome_tribunal(self, planilha: DataFrame, pasta_trabalho: str) -> DataFrame:
        # Define o nome do tribunal com base no nome da pasta de trabalho
        pastas_trabalho: Dict[str, str] = {
            "080001TRIBUNAL SUPERIOR DO TRA": "Tribunal Superior do Trabalho",
            "080009TRIBUNAL REGIONAL DO TRA": "Tribunal Regional do Trabalho - 1ª Região",
            "080010TRIBUNAL REGIONAL DO TRA": "Tribunal Regional do Trabalho - 2ª Região",
            "080008TRIBUNAL REGIONAL DO TRA": "Tribunal Regional do Trabalho - 3ª Região",
            "080014TRIBUNAL REGIONAL DO TRA": "Tribunal Regional do Trabalho - 4ª Região",
            "080007TRIBUNAL REGIONAL DO TRA": "Tribunal Regional do Trabalho - 5ª Região",
            "080006TRIBUNAL REGIONAL DO TRA": "Tribunal Regional do Trabalho - 6ª Região",
            "080004TRIBUNAL REGIONAL DO TRA": "Tribunal Regional do Trabalho - 7ª Região",
            "080003TRIBUNAL REGIONAL DO TRA": "Tribunal Regional do Trabalho - 8ª Região",
            "080012TRIBUNAL REGIONAL DO TRA": "Tribunal Regional do Trabalho - 9ª Região",
            "080016TRIBUNAL REGIONAL DO TRA": "Tribunal Regional do Trabalho - 10ª Região",
            "080002TRIBUNAL REGIONAL DO TRA": "Tribunal Regional do Trabalho - 11ª Região",
            "080013TRIBUNAL REGIONAL DO TRA": "Tribunal Regional do Trabalho - 12ª Região",
            "080005TRIBUNAL REGIONAL DO TRA": "Tribunal Regional do Trabalho - 13ª Região",
            "080015TRIBUNAL REGIONAL DO TRA": "Tribunal Regional do Trabalho - 14ª Região",
            "080011TRIBUNAL REGIONAL DO TRA": "Tribunal Regional do Trabalho - 15ª Região",
            "080018TRIBUNAL REGIONAL DO TRA": "Tribunal Regional do Trabalho - 16ª Região",
            "080019TRIBUNAL REGIONAL DO TRA": "Tribunal Regional do Trabalho - 17ª Região",
            "080020TRIBUNAL REGIONAL DO TRA": "Tribunal Regional do Trabalho - 18ª Região",
            "080022TRIBUNAL REGIONAL DO TRA": "Tribunal Regional do Trabalho - 19ª Região",
            "080023TRIBUNAL REGIONAL DO TRA": "Tribunal Regional do Trabalho - 20ª Região",
            "080021TRIBUNAL REGIONAL DO TRA": "Tribunal Regional do Trabalho - 21ª Região",
            "080024TRIBUNAL REGIONAL DO TRA": "Tribunal Regional do Trabalho - 22ª Região",
            "080025TRIBUNAL REGIONAL DO TRA": "Tribunal Regional do Trabalho - 23ª Região",
            "080026TRIBUNAL REGIONAL DO TRA": "Tribunal Regional do Trabalho - 24ª Região",
        }
        nome_tribunal: str = pastas_trabalho[pasta_trabalho]
        planilha.Name = nome_tribunal
        return planilha

    def __set__ano_quadrimestre(self, planilha: DataFrame) -> None:
        # Define o ano e o quadrimestre da planilha
        if self.exercicio is None or self.periodo is None:
            colunas: List[str] = planilha.columns.tolist()
            mascara: str = r"^[A-Z]{3}/20[0-9]{2}"
            periodo: str = ""

            for coluna in colunas:
                match = re.match(mascara, coluna)
                if match:
                    periodo = coluna
            periodo = periodo.capitalize()
            data_formatada: datetime = datetime.strptime(periodo, "%b/%Y")
            mes: int = data_formatada.month
            self.exercicio = data_formatada.year
            self.periodo = floor((mes - 1) // 3)
            
    def __processar_planilhas(self) -> None:
        # Processa todas as planilhas não formatadas
        for pasta_atual, planilha_df in self.planilhas_TG_NAO_FORMATADAS.items():
            planilha: DataFrame = self.__definir_planilha(planilha_df, pasta_atual)
            self.planilhas_TG.append(planilha)

    def __abrir_planilhas(self, caminho_planilhas: str) -> None:
        # Abre as planilhas do caminho especificado
        with open(caminho_planilhas, 'rb') as file:
            self.planilhas_TG_NAO_FORMATADAS = pd.read_excel(file, sheet_name=None, engine='openpyxl')
