from dataclasses import dataclass

@dataclass
class Talhao:
    id: int
    nome: str
    hectares: float
    produtividade_esperada_t_ha: float


@dataclass
class Colheita:
    talhao_id: int
    talhao_nome: str
    esperado_t: float
    colhido_t: float
    perda_percentual: float
    classificacao: str
    enviado_oracle: bool = False