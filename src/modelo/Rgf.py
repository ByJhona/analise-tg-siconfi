

class Rgf():
    exercicio: int
    periodo: int
    periodicidade: str
    instituicao: str
    cod_ibge: int
    uf: str
    co_poder: str
    populacao: str
    anexo: str
    esfera: str
    rotulo: str
    coluna: str
    cod_conta: str
    conta: str
    valor: str
    
    def __init__(self, exercicio, periodo, periodicidade, instituicao, cod_ibge, uf, co_poder, populacao, anexo, esfera, rotulo, coluna, cod_conta, conta, valor):
        self.exercicio = exercicio
        self.periodo = periodo
        self.periodicidade = periodicidade
        self.instituicao = instituicao
        self.cod_ibge = cod_ibge
        self.uf = uf
        self.co_poder = co_poder
        self.populacao = populacao
        self.anexo = anexo
        self.esfera = esfera
        self.rotulo = rotulo
        self.coluna = coluna
        self.cod_conta = cod_conta
        self.conta = conta
        self.valor = valor

    def __str__(self):
        return f'{self.exercicio} {self.periodo} {self.periodicidade} {self.instituicao} {self.conta} {self.coluna} {self.valor}'
        #return f'{self.exercicio} {self.periodo} {self.periodicidade} {self.instituicao} {self.uf} {self.co_poder} {self.populacao} {self.anexo} {self.rotulo} {self.coluna} {self.cod_conta} {self.conta} {self.valor}'

    