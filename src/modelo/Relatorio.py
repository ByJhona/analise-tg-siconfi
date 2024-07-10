from typing import NamedTuple
import pandas as pd
from UliPlot.XLSX import auto_adjust_xlsx_column_width

from modelo import Rgf
from modelo.Planilha import Planilha


class Relatorio():
    @classmethod
    def construir_relatorio(cls, caminho, planilhas:list[pd.DataFrame], mescla:list[pd.DataFrame], ano, quadrimestre):
        nome_arquivo = f"{caminho}/Relatório {quadrimestre}-{ano}.xlsx"
        dict_mescla = Planilha.criar_dicionario_planilhas(mescla)

        with pd.ExcelWriter(nome_arquivo, engine='openpyxl') as writer:
        
            for dif in planilhas:
                nome = dif.Name
                info = pd.DataFrame(columns=["Informações"], data=[nome, f"Ano: {ano}", f"Quadrimestre: {quadrimestre}"])            
                dif = dif.loc[(dif != "R$ 0.00").any(axis=1)]
                dif = dif.loc[ :,(dif != "R$ 0.00").any(axis=0)]

                dif.Name = nome
                nome = cls.__abreviacao_nome_tribunal(nome)
           
                proxima_linha = len(info.index) + 2


                
                info.to_excel(writer, sheet_name=nome, index=False)
                #dif_estilo = dif.style.map(cls.corir_celulas)
                #dif_estilo = dif.style.map()
                

                dif.to_excel( writer, startrow=proxima_linha, sheet_name=nome)

                teste = dict_mescla[dif.Name]
                teste.to_excel(writer, startrow=len(dif.index) + len(info.index) + 10, sheet_name=nome)
            
                
                auto_adjust_xlsx_column_width(dif, writer, sheet_name=nome, margin=0)
               #auto_adjust_xlsx_column_width(teste, writer, sheet_name=nome, margin=0)
            writer.close
    @staticmethod
    def corir_celulas(val):
        if val < 0:
            cor = '#F4A460'
        elif val > 0:
            cor = '#F0E68C'
        else:
            cor = '#8FBC8F'
        
        return f'background-color: {cor}'

    @classmethod
    def __abreviacao_nome_tribunal(cls, nome):
        if len(nome) > 30:
            nome = f"TRT {nome[30:]}"
        else:
            nome = "TST"
        return nome
        

