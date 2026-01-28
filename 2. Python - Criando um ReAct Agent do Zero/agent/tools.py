def verificar_fatores_risco(sintoma):
    """Verifica se um sintoma está entre os alertas do SobreVidas para câncer de boca."""

    alertas = ["mancha branca", "ferida que não cicatriza", "nódulo no pescoço", "rouquidão persistente"]
    
    if sintoma.lower() in alertas:
        return "Alerta: Este sintoma requer avaliação profissional prioritária na plataforma SobreVidas."
        
    return "Sintoma não catalogado como alerta imediato, mas recomenda-se consulta de rotina."


def suporte_paliativo(sintoma_especifico):
    """
    Fornece orientações de conforto para pacientes em cuidados paliativos.
    """

    orientacoes = {
        "boca seca": "Use saliva artificial e aumente a ingestão de água em pequenos goles.",
        "dor na mastigação": "Prefira alimentos pastosos e em temperatura morna/fria.",
        "dificuldade de higienização": "Use escovas de cerdas extra macias ou gazes umedecidas com soro."
    }

    return orientacoes.get(sintoma_especifico.lower(), "Consulte a equipe de enfermagem do SobreVidas para este sintoma específico.")


def triagem_prioridade(tempo_lesao_dias):
    """
    Define a prioridade de encaminhamento baseada no tempo de lesão.
    Retorna o nível de urgência para a Rede de Atenção à Saúde.
    """
    tempo = int(tempo_lesao_dias)

    if tempo > 15:
        return "ALTA PRIORIDADE: Encaminhar para uma Unidade Básica de Saúde imediatamente."

    elif tempo > 7:
        return "MÉDIA PRIORIDADE: Encaminhar para uma Unidade Básica de Saúde em 7 dias."

    return "BAIXA PRIORIDADE: Orientar suspensão de fatores de risco e reavaliar em 15 dias."