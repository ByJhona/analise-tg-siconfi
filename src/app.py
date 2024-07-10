# Importa as classes PlanilhaSICONFI, PlanilhaTG, Planilha, Relatorio do módulo modelo, e a biblioteca pandas
from modelo.PlanilhaSICONFI import PlanilhaSICONFI
from modelo.PlanilhaTG import PlanilhaTG

from modelo.Planilha import Planilha
from modelo.Relatorio import Relatorio
import pandas as pd

# Define o caminho para o arquivo Excel que contém as planilhas
caminho_planilhas = r"C:\Users\e008494\Desktop\tg_siconfi\planilhas\RGF - GERAL.xlsx"
caminho_salvar_relatorio = r"C:\Users\e008494\Desktop\tg_siconfi\planilhas"

def main():
    # Cria uma instância da classe PlanilhaTG, passando o caminho do arquivo como argumento
    obj_tg = PlanilhaTG(caminho_planilhas)
    
    # Cria uma instância da classe PlanilhaSICONFI, utilizando os atributos 'exercicio' e 'periodo' da instância obj_tg
    obj_siconfi = PlanilhaSICONFI(obj_tg.exercicio, obj_tg.periodo)

    # Obtém as planilhas TG da instância obj_tg
    planilhas_tg = obj_tg.planilhas_TG
    
    # Obtém as planilhas SICONFI da instância obj_siconfi
    planilhas_siconfi = obj_siconfi.planilhas_SICONFI

    # Normaliza as planilhas TG e SICONFI, ajustando seus formatos para comparação
    planilhas_tg, planilhas_siconfi = Planilha.normalizar_planilhas(planilhas_tg, planilhas_siconfi)
    
    # Subtrai os valores das planilhas TG e SICONFI para identificar diferenças
    diferencas = Planilha.subtrair_planilhas(planilhas_tg, planilhas_siconfi)
    mesclado = Planilha.mesclar_planilhas(planilhas_tg, planilhas_siconfi)

    # Constrói um relatório com as diferenças identificadas, usando o exercício e o período das planilhas
    Relatorio.construir_relatorio(caminho_salvar_relatorio, diferencas, mesclado,obj_tg.exercicio, obj_tg.periodo)

    pass

if __name__ == "__main__":
    main()
