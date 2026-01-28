from dotenv import load_dotenv
from groq import Groq
import os
import re

from agent.tools import verificar_fatores_risco, suporte_paliativo, triagem_prioridade
from agent.system_prompt import SYSTEM_PROMPT


# 1. CONFIGURAÇÕES INICIAIS
# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()


# Inicializa o cliente da Groq para fazer chamadas à API
client = Groq(
    api_key=os.environ.get("GROQ_API_KEY"),
)


# 2. AGENTE
class Agent:
    def __init__(self, client: Groq, system):
        """
        Inicializa o agente, um prompt e uma lista de mensagens para manter o histórico da conversa.
        """

        self.client = client
        self.system = system
        self.messages = []
        if self.system is not None:
            self.messages.append({"role": "system", "content": self.system})

    def __call__(self, message=""):
        """
        Permite chamar o agente como uma função: agent("pergunta").
        Gerencia o histórico e chama o método execute.
        """

        if message:
            self.messages.append({"role": "user", "content": message})
        result = self.execute()
        self.messages.append({"role": "assistant", "content": result})
        return result

    def execute(self):
        """
        Envia todo o histórico de mensagens para o agente e retorna a resposta.
        """

        completion = self.client.chat.completions.create(
            messages=self.messages,
            model="llama-3.3-70b-versatile",
        )
        return completion.choices[0].message.content


def agent_loop(max_iterations, query):
    """
    Automatiza o processo de: 
    1. Perguntar ao agente.
    2. Identificar se ele quer usar uma ferramenta (Action).
    3. Executar a ferramenta e devolver o resultado (Observation).
    4. Repetir até obter o "Answer".
    """

    agent = Agent(client, SYSTEM_PROMPT)
    tools = {
        'verificar_fatores_risco': verificar_fatores_risco,
        'suporte_paliativo': suporte_paliativo,
        'triagem_prioridade': triagem_prioridade
    }

    historico_log = [f"QUERY DO USUÁRIO: {query}\n" + "="*50 + "\n"]

    next_prompt = query
    i = 0

    while i < max_iterations:
        i += 1
        result = agent(next_prompt)
        historico_log.append(f"PASSO {i}:\n{result}")
        print(result)

        # Verifica se o modelo quer executar uma ação
        if "PAUSE" in result and "Action" in result:

            # Regex para extrair o nome da ferramenta e o argumento
            action = re.findall(r"Action:\s*([a-z_]+):\s*(.+)", result, re.IGNORECASE)
            
            if action:  
                chosen_tool = action[0][0]
                arg = action[0][1]

            if chosen_tool in tools:
                # Executa a função Python
                result_tool = tools[chosen_tool](arg)
                next_prompt = f"Observation: {result_tool}"

            else:
                next_prompt = f"Observation: Tool {chosen_tool} not found"

            historico_log.append(f"\n>>> {next_prompt}\n")
            print(next_prompt)

            # Volta para o início do loop com a observação
            continue

        # Para o loop quando o agente tiver a resposta final
        if "Answer" in result:
            break

    # Geração de um Relatório com a análise do Agente
    nome_arquivo = "2. Python - Criando um ReAct Agent do Zero/relatorio_sobrevidas.txt"
    with open(nome_arquivo, "w", encoding="utf-8") as f:
        f.write("\n".join(historico_log))
    
    print(f"\n" + "="*50)
    print(f"RELATÓRIO GERADO: {nome_arquivo}")
    print("="*50)


# EXECUÇÃO DO AGENTE
agent_loop(10, "Tenho uma ferida que não cicatriza há 20 dias e minha boca está seca. O que devo fazer?")