import os
import pandas as pd
import locale
import requests
from modelo.Rgf import Rgf


locale.setlocale(locale.LC_ALL, "pt_BR.utf8")
os.environ["no_proxy"] = "*"

class PlanilhaSICONFI:
    """Classe para manipulação e análise de planilhas SICONFI."""

    def __init__(self, ano, quadrimestre):
        self.planilhas_SICONFI = []
        ##
        self.exercicio = ano
        self.periodo = quadrimestre
        self.periodicidade = "Q"
        self.cod_ibge = "1"
        self.uf = "BR"
        self.co_poder = "J"
        self.co_tipo_demonstrativo = "RGF"
        self.anexo = "RGF-Anexo 01"
        self.esfera = "U"
        self.rotulo = "Padrão"
        ##
        self.__construir_planilha_siconfi()

    ############################################### SICONFI

    def __buscar_rgf(self) -> list[Rgf]:
        """Busca os dados de RGF a partir da API do SICONFI."""
        url = (
            f"https://apidatalake.tesouro.gov.br/ords/siconfi/tt/rgf?"
            f"an_exercicio={self.exercicio}&"
            f"in_periodicidade={self.periodicidade}&"
            f"nr_periodo={self.periodo}&"
            f"co_tipo_demonstrativo={self.co_tipo_demonstrativo}&"
            f"no_anexo={self.anexo}&"
            f"co_esfera={self.esfera}&"
            f"co_poder={self.co_poder}&"
            f"id_ente={self.cod_ibge}"
        )
        rgfs = []

        while True:
            response = requests.get(url)
            response_rgf = response.json()
            items = response_rgf.get("items", [])
            has_more = response_rgf.get("hasMore", False)
            links = response_rgf.get("links", [])

            url = self.__buscar_proxima_pagina(has_more, links)

            tribunais = self.__get_tribunais()

            for item in items:
                if item["instituicao"] in tribunais:
                    rgfs.append(
                        Rgf(
                            item["exercicio"],
                            item["periodo"],
                            item["periodicidade"],
                            item["instituicao"],
                            item["cod_ibge"],
                            item["uf"],
                            item["co_poder"],
                            item["populacao"],
                            item["esfera"],
                            item["anexo"],
                            item["rotulo"],
                            item["coluna"],
                            item["cod_conta"],
                            item["conta"],
                            item["valor"],
                        )
                    )

            if not has_more:
                break

        return rgfs

    def __buscar_proxima_pagina(self, has_more: bool, links: list) -> str:
        """Busca a URL da próxima página de resultados."""
        if has_more:
            for link in links:
                if link["rel"] == "next":
                    return link["href"]
        return ""

    def __definir_12_meses_anteriores(self) -> list[str]:
        """Define os últimos 12 meses de referência com base no quadrimestre atual."""
        ano = self.exercicio
        quadrimestre = self.periodo
        mes = 4 * quadrimestre
        meses = [
            "JAN", "FEV", "MAR", "ABR", "MAI", "JUN",
            "JUL", "AGO", "SET", "OUT", "NOV", "DEZ"
        ]
        meses_anteriores = []

        for i in range(12):
            anterior = (mes - i - 1) % 12
            ano_anterior = ano if mes - i > 0 else ano - 1
            meses_anteriores.append(f"{meses[anterior]}/{ano_anterior}")

        return meses_anteriores

    def __definir_colunas_referencia(self) -> dict:
        """Define as colunas de referência para a planilha."""
        meses = self.__definir_12_meses_anteriores()
        dict_colunas_siconfi = {
            f"<MR-{i}>" if i != 0 else "<MR>": meses[i] for i in range(12)
        }
        dict_colunas_siconfi["TOTAL (ÚLTIMOS 12 MESES) (a)"] = "TOTAL"
        dict_colunas_siconfi["INSCRITAS EM RESTOS A PAGAR NÃO PROCESSADOS (b)"] = "RPNP"
        return dict_colunas_siconfi

    def __get_conta(self, conta: str) -> str:
        """Retorna a conta correspondente para uma determinada descrição."""
        contas = {
            "DESPESA BRUTA COM PESSOAL (I)": "DESPESA BRUTA COM PESSOAL (I)",
            "Pessoal Ativo": "I.01. Pessoal Ativo",
            "Vencimentos, Vantagens e Outras Despesas Variáveis": "I.01.1. Vencimentos, Vantagens e Outras Despesas Variáveis",
            "Obrigações Patronais": "I.01.2. Obrigações Patronais",
            "Pessoal Inativo e Pensionistas": "I.02. Pessoal Inativo e Pensionistas 2024",
            "Aposentadorias, Reserva e Reformas": "I.02.1. Aposentadorias, Reserva e Reformas",
            "Pensões": "I.02.2. Pensões",
            "Outras Despesas de Pessoal decorrentes de Contratos de Terceirização ou de contratação de forma indireta (§ 1º do art. 18 da LRF)": "I.03. Outras despesas de pessoal decorrentes de contratos de terceirização ou de contratação de forma indireta (§ 1º do art. 18 da LRF)",
            "Despesa com Pessoal não Executada Orçamentariamente": "Despesa com Pessoal não Executada Orçamentariamente",
            "DESPESAS NÃO COMPUTADAS (§ 1º do art. 19 da LRF) (II)": "DESPESAS NÃO COMPUTADAS (II) (§ 1º do art. 19 da LRF)",
            "Indenizações por Demissão e Incentivos à Demissão Voluntária": "II.01. Indenizações por Demissão e Incentivos à Demissão Voluntária",
            "Decorrentes de Decisão Judicial de Período Anterior ao da Apuração": "II.02.Decorrentes de Decisão Judicial de período anterior ao da apuração",
            "Despesas de Exercícios Anteriores de Período Anterior ao da Apuração": "II.03.Despesas de Exercícios Anteriores de período anterior ao da apuração",
            "Inativos e Pensionistas com Recursos Vinculados": "II.04.Inativos e Pensionistas com Recursos Vinculados",
            "DESPESA LÍQUIDA COM PESSOAL (III) = (I - II)": "DESPESA LÍQUIDA COM PESSOAL (III) = (I - II)",
        }
        return contas.get(conta, "")

    def __get_tribunais(self):
        return  [
        "Tribunal Regional do Trabalho - 1ª Região",
        "Tribunal Regional do Trabalho - 2ª Região",
        "Tribunal Regional do Trabalho - 3ª Região",
        "Tribunal Regional do Trabalho - 4ª Região",
        "Tribunal Regional do Trabalho - 5ª Região",
        "Tribunal Regional do Trabalho - 6ª Região",
        "Tribunal Regional do Trabalho - 7ª Região",
        "Tribunal Regional do Trabalho - 8ª Região",
        "Tribunal Regional do Trabalho - 9ª Região",
        "Tribunal Regional do Trabalho - 10ª Região",
        "Tribunal Regional do Trabalho - 11ª Região",
        "Tribunal Regional do Trabalho - 12ª Região",
        "Tribunal Regional do Trabalho - 13ª Região",
        "Tribunal Regional do Trabalho - 14ª Região",
        "Tribunal Regional do Trabalho - 15ª Região",
        "Tribunal Regional do Trabalho - 16ª Região",
        "Tribunal Regional do Trabalho - 17ª Região",
        "Tribunal Regional do Trabalho - 18ª Região",
        "Tribunal Regional do Trabalho - 19ª Região",
        "Tribunal Regional do Trabalho - 20ª Região",
        "Tribunal Regional do Trabalho - 21ª Região",
        "Tribunal Regional do Trabalho - 22ª Região",
        "Tribunal Regional do Trabalho - 23ª Região",
        "Tribunal Regional do Trabalho - 24ª Região",
        "Tribunal Superior do Trabalho",
    ]

    def __construir_planilha_siconfi(self):
        dict_planilhas = self.__criar_dicionario_planilhas_rgf()

        for t, data in dict_planilhas.items():
            df = pd.DataFrame.from_dict(data, orient="index")
            df.Name = t
            self.planilhas_SICONFI.append(df)

    def __criar_dicionario_planilhas_rgf(self):
        """Constrói a planilha SICONFI a partir dos dados obtidos."""
        rgfs = self.__buscar_rgf()
        dict_colunas_referencia = self.__definir_colunas_referencia()
        dict_tribunais = {}

        for rgf in rgfs:
            key = rgf.instituicao
            if key not in dict_tribunais:
                dict_tribunais[key] = {}
            conta = self.__get_conta(rgf.conta)

            if conta not in dict_tribunais[key]:
                dict_tribunais[key][conta] = {}
            coluna = dict_colunas_referencia.get(rgf.coluna)
            if coluna:
                dict_tribunais[key][conta][coluna] = rgf.valor
        return dict_tribunais
