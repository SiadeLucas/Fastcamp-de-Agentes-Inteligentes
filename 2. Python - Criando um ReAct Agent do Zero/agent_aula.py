from dotenv import load_dotenv
from groq import Groq
import os


# 1. CONFIGURAÇÕES INICIAIS
# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()


# Inicializa o cliente da Groq para fazer chamadas à API
client = Groq(
    api_key=os.environ.get("GROQ_API_KEY"),
)


# Quickstart do Groq
# chat_completion = client.chat.completions.create(
#     messages=[
#         {
#             "role": "user",
#             "content": "Explain the importance of fast language models",
#         }
#     ],
#     model="llama-3.3-70b-versatile",
# )

# print(chat_completion.choices[0].message.content)


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


# 3. PROMPT DO AGENTE (ReAct)
# Este prompt ensina o modelo a seguir o fluxo: 
# Thought -> Action -> PAUSE -> Observation
system_prompt = """
You run in a loop of Thought, Action, PAUSE, Observation.
At the end of the loop you output an Answer
Use Thought to describe your thoughts about the question you have been asked.
Use Action to run one of the actions available to you - then return PAUSE.
Observation will be the result of running those actions.

Your available actions are:

calculate:
e.g. calculate: 4 * 7 / 3
Runs a calculation and returns the number - uses Python so be sure to use floating point syntax if necessary

get_planet_mass:
e.g. get_planet_mass: Earth
returns weight of the planet in kg

Example session:

Question: What is the mass of Earth times 2?
Thought: I need to find the mass of Earth
Action: get_planet_mass: Earth
PAUSE 

You will be called again with this:

Observation: 5.972e24

Thought: I need to multiply this by 2
Action: calculate: 5.972e24 * 2
PAUSE

You will be called again with this: 

Observation: 1,1944×10e25

If you have the answer, output it as the Answer.

Answer: The mass of Earth times 2 is 1,1944×10e25.

Now it's your turn:
""".strip()


# 4. FERRAMENTAS
def calculate(operation):
    """
    Executa uma operação matemática.
    """

    return eval(operation)

def get_planet_mass(planet) -> float:
    """
    Retorna a massa de um planeta.
    """

    match planet.lower():
        case "earth":
            return 5.972e24
        case "mars":
            return 6.39e23
        case "jupiter":
            return 1.898e27
        case "saturn":
            return 5.683e26
        case "uranus":
            return 8.681e25
        case "neptune":
            return 1.024e26
        case "mercury":
            return 3.285e23
        case "venus":
            return 4.867e24
        case _:
            return 0.0


# EXEMPLO DE EXECUÇÃO (MANUAL)
# neil_tyson = Agent(client, system_prompt)

# result = neil_tyson("What is the mass of Earth times 5?")
# print(result)

# print("\n", neil_tyson.messages)

# result = neil_tyson()
# print("\n", result)

# observation = get_planet_mass("Earth")
# print("\n", observation)

# next_prompt = f"Observation: {observation}"
# result = neil_tyson(next_prompt)
# print("\n", result)

# print("\n", neil_tyson.messages)

# result = neil_tyson()
# print("\n", result)

# observation = calculate("5.972e24 * 5")
# print("\n", observation)

# next_prompt = f"Observation: {observation}"
# result = neil_tyson(next_prompt)
# print("\n", result)

# print("\n", neil_tyson.messages)


# EXEMPLO DE EXECUÇÃO (AUTOMATIZADO)
import re

def agent_loop(max_iterations, system, query):
    """
    Automatiza o processo de: 
    1. Perguntar ao agente.
    2. Identificar se ele quer usar uma ferramenta (Action).
    3. Executar a ferramenta e devolver o resultado (Observation).
    4. Repetir até obter o "Answer".
    """

    agent = Agent(client, system_prompt)
    tools = ['calculate', 'get_planet_mass']
    next_prompt = query
    i = 0

    while i < max_iterations:
        i += 1
        result = agent(next_prompt)
        print(result)

        # Verifica se o modelo quer executar uma ação
        if "PAUSE" in result and "Action" in result:

            # Regex para extrair o nome da ferramenta e o argumento
            action = re.findall(r"Action: ([a-z_]+): (.+)", result, re.IGNORECASE)
            chosen_tool = action[0][0]
            arg = action[0][1]

            if chosen_tool in tools:
                # Executa a função Python
                result_tool = eval(f"{chosen_tool}('{arg}')")
                next_prompt = f"Observation: {result_tool}"

            else:
                next_prompt = f"Observation: Tool {chosen_tool} not found"

            print(next_prompt)

            # Volta para o início do loop com a observação
            continue

        # Para o loop quando o agente tiver a resposta final
        if "Answer" in result:
            break


# EXECUÇÃO DO AGENTE
agent_loop(10, system_prompt, "What is the mass of the Earth plus the mass of Mercury, and all of it times 5?")