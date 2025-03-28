import time
import os
import random
import pickle
from enum import Enum
from datetime import datetime, timedelta

# Definição das classes (1/3)
class Mineral:
    def __init__(self, nome, valor, icon):
        self.nome = nome
        self.valor = valor
        self.icon = icon

class Planeta:
    def __init__(self, nome, minerais, dificuldade, eventos):
        self.nome = nome
        self.minerais = minerais
        self.dificuldade = dificuldade
        self.eventos = eventos
        self.riqueza = {mineral.nome: random.randint(100, 250) for mineral in minerais}
        self.evento_ativo = None
        self.tempo_evento = 0
        self.ultima_atualizacao = time.time()  # Novo atributo para controlar o tempo

    def verificar_evento(self):
        # 20% de chance de um evento ocorrer
        if random.random() < 0.2 and not self.evento_ativo:
            self.evento_ativo = random.choice(self.eventos)
            self.tempo_evento = 30  # 30 segundos
            self.ultima_atualizacao = time.time()  # Registra o momento do início
            return self.evento_ativo
        return None

    def atualizar_evento(self):
        if self.evento_ativo and self.tempo_evento > 0:
            agora = time.time()
            tempo_decorrido = agora - self.ultima_atualizacao

            # Só atualiza se passou pelo menos 1 segundo
            if tempo_decorrido >= 1:
                segundos_passados = int(tempo_decorrido)
                self.tempo_evento = max(0, self.tempo_evento - segundos_passados)
                self.ultima_atualizacao = agora  # Reinicia o contador

                if self.tempo_evento <= 0:
                    self.evento_ativo = None

class Mochila:
    def __init__(self, capacidade=500):
        self.capacidade = capacidade
        self.conteudo = {}  # {nome_mineral: quantidade}
        self.creditos_estimados = 0

    def adicionar_mineral(self, mineral, quantidade):
        #Adiciona mineral à mochila
        if isinstance(mineral, Mineral):
            nome_mineral = mineral.nome
        else:
            nome_mineral = mineral

        total_itens = sum(self.conteudo.values()) + quantidade

        if total_itens <= self.capacidade:
            self.conteudo[nome_mineral] = self.conteudo.get(nome_mineral, 0) + quantidade
            return True
        return False

    def remover_mineral(self, mineral, quantidade):
        #Remove mineral da mochila
        nome_mineral = mineral.nome if isinstance(mineral, Mineral) else mineral

        if nome_mineral in self.conteudo and self.conteudo[nome_mineral] >= quantidade:
            self.conteudo[nome_mineral] -= quantidade
            if self.conteudo[nome_mineral] <= 0:
                del self.conteudo[nome_mineral]
            return True
        return False

    def calcular_valor_total(self):
        #Calcula valor total de todos os minerais em créditos
        total = 0
        for nome_mineral, qtd in self.conteudo.items():
            mineral_obj = next((m for m in MINERAIS_DISPONIVEIS if m.nome == nome_mineral), None)
            if mineral_obj:
                total += qtd * mineral_obj.valor
        self.creditos_estimados = total
        return total

class Nave:
    def __init__(self):
        self.combustivel = 100
        self.combustivel_max = 100
        self.velocidade = 1
        self.capacidade_mineracao = 1
        self.dano = 0  # 0-100, se chegar a 100 a nave é destruída
        self.upgrades = {
            "motor_fusao": True, #Necessário para ir até Andrômeda
            "escudo_antimat": False,
            "traje_avancado": False
        }

    def minerar(self, planeta, mineral_alvo):
        """
        Método unificado de mineração - versão simplificada
        Retorna a quantidade minerada (0 se falhar)
        """
        # Verificações de segurança
        if not hasattr(planeta, 'riqueza') or mineral_alvo.nome not in planeta.riqueza:
            return 0

        if planeta.riqueza[mineral_alvo.nome] <= 0:
            print(f"⚠️ {mineral_alvo.nome} esgotado!")
            return 0

        # Cálculo da quantidade
        try:
            base = random.randint(10, 20)
            quantidade = base * self.capacidade_mineracao

            # Aplica efeitos de eventos
            if hasattr(planeta, 'evento_ativo') and planeta.evento_ativo == "Tempestade de areia":
                quantidade = int(quantidade * 0.7)

            # Garante não ultrapassar o disponível
            quantidade = min(quantidade, planeta.riqueza[mineral_alvo.nome])
            planeta.riqueza[mineral_alvo.nome] -= quantidade

            # Mensagem única simplificada
            if quantidade > 0:
                print(f"⛏️ Você minerou {quantidade} unidades de {mineral_alvo.nome}!")
                if planeta.riqueza[mineral_alvo.nome] <= 0:
                    print(f"⚡ {mineral_alvo.nome} esgotado!")

            return quantidade

        except Exception:
            return 0

    def viajar(self, custo):
        custo_ajustado = custo / self.velocidade
        if self.combustivel >= custo_ajustado:
            self.combustivel -= custo_ajustado
            return True
        return False

    def estacao_espacial(jogador):
        print("\n*Docking na Estação Forja Estelar...*")
        print("\"Salve, humano! Recarrego combustível por créditos. De quanto precisa?\"")

        while True:
            print(f"\n💰 Seus créditos: {jogador.creditos}")
            print(
                f"🔋 Combustível atual: {int(jogador.nave.combustivel)}/{jogador.nave.combustivel_max}")
            print("\n1. Recarregar 100% combustível (5000 créditos)")
            print("2. Recarregar 20% combustível (1000 créditos)")
            print("3. Sair da estação")

            escolha = input("\nEscolha: ").strip()

            if escolha == "1":
                custo = 5000
                if jogador.creditos >= custo:
                    jogador.creditos -= custo
                    jogador.nave.combustivel = jogador.nave.combustivel_max
                    print(f"\n🔋 Combustível recarregado para 100%! (-{custo} créditos)")
                    print(f"💰 Créditos restantes: {jogador.creditos}")
                else:
                    print(f"\n⚠️ Você precisa de {custo} créditos (você tem: {jogador.creditos})")
                time.sleep(1.5)

            elif escolha == "2":
                custo = 1000
                if jogador.creditos >= custo:
                    jogador.creditos -= custo
                    recarga = jogador.nave.combustivel_max * 0.2
                    jogador.nave.combustivel = min(jogador.nave.combustivel + recarga,
                                                   jogador.nave.combustivel_max)
                    print(f"\n🔋 Combustível recarregado em 20%! (-{custo} créditos)")
                    print(f"💰 Créditos restantes: {jogador.creditos}")
                else:
                    print(f"\n⚠️ Você precisa de {custo} créditos (você tem: {jogador.creditos})")
                time.sleep(1.5)

            elif escolha == "3":
                print("\n*Desacoplando da estação...*")
                time.sleep(1)
                break

            else:
                print("\nOpção inválida!")
                time.sleep(1)

    def reparar(self, quantidade):
        self.dano = max(0, self.dano - quantidade)

    def aplicar_evento(self, evento, jogador):
        try:
            if evento == "Falha no Traje":
                if not self.upgrades.get("traje_avancado", False):
                    minerais = list(jogador.mochila.conteudo.items())
                    if minerais:
                        total_perdido = 0
                        for mineral, qtd in minerais:
                            perdido = max(1, int(qtd * 0.1))
                            jogador.mochila.remover_mineral(mineral, perdido)
                            total_perdido += perdido
                        return f"⚠️ ALERTA! Vazamento no traje. Perdidos {total_perdido} minérios!"
                    return "⚠️ ALERTA! Vazamento no traje. (Sem minérios para perder)"
                return "Traje espacial intacto (upgrade ativado)"

            elif evento == "Vazamento de O₂":
                escolha = input("Vazamento detectado! Perder [1] 15% combustível ou [2] 5 Hélio-3? ")
                if escolha == "2" and jogador.mochila.conteudo.get("Hélio-3", 0) >= 5:
                    jogador.mochila.remover_mineral("Hélio-3", 5)
                    return "⚡ Perdeu 5 Hélio-3 para conter vazamento"
                else:
                    perdido = int(jogador.nave.combustivel * 0.15)
                    jogador.nave.combustivel -= perdido
                    return f"⛽ Perdeu {perdido} combustível no vazamento"

            elif evento == "Areia Movediça":
                print("⏳ Solo instável! Você afundou na areia movediça (20s)...")
                time.sleep(20)
                return "✅ Conseguiu se libertar da areia movediça!"

            elif evento == "Asteroide Próximo":
                if self.upgrades.get("escudo_antimat", False):
                    return "🛡️ Os escudos desviaram o asteroide!"
                self.dano = min(self.dano + 50, 100)
                return "💥 Asteroide atingiu a nave! -50% integridade"

            return f"Evento desconhecido: {evento}"

        except Exception as e:
            print(f"Erro no evento: {str(e)}")
            return "⚡ Evento interrompido"

class Jogador:
    def __init__(self, nome):
        self.nome = nome
        self.nave = Nave()
        self.mochila = Mochila()
        self.creditos = 5000
        self.experiencia = 0
        self.nivel = 1
        self.localizacao = "Helios Reach"
        self.planeta_atual = None
        self.planetais_visitados = set()
        self.planetais_descobertos = set()

    def ganhar_experiencia(self, quantidade):
        self.experiencia += quantidade
        if self.experiencia >= 100:
            self.nivel += 1
            self.experiencia -= 100
            return True
        return False

    def vender_minerais(self):
        #Vende qualquer tipo de mineral
        if not self.mochila.conteudo:
            print("⚠️ Mochila vazia!")
            return 0

        print("\n📦 Minerais disponíveis para venda:")
        minerais_disponiveis = list(self.mochila.conteudo.items())

        for i, (nome, qtd) in enumerate(minerais_disponiveis, 1):
            mineral_obj = next((m for m in MINERAIS_DISPONIVEIS if m.nome == nome), None)
            if mineral_obj:
                valor = qtd * mineral_obj.valor
                print(f"{i}. {mineral_obj.icon} {nome}: {qtd} unidades (Valor: {valor} créditos)")
            else:
                print(f"{i}. ❓ {nome}: {qtd} unidades (Valor desconhecido)")

        try:
            opcao = int(input("Escolha o mineral para vender (0 para cancelar): ")) - 1
            if opcao == -1:
                return 0

            if 0 <= opcao < len(minerais_disponiveis):
                nome_mineral, qtd_disponivel = minerais_disponiveis[opcao]
                qtd_vender = int(input(f"Quantidade de {nome_mineral} para vender (max {qtd_disponivel}): "))

                if 0 < qtd_vender <= qtd_disponivel:
                    mineral_obj = next((m for m in MINERAIS_DISPONIVEIS if m.nome == nome_mineral), None)
                    if mineral_obj:
                        valor = qtd_vender * mineral_obj.valor
                        if self.mochila.remover_mineral(nome_mineral, qtd_vender):
                            self.creditos += valor
                            print(f"💰 Vendido {qtd_vender} de {nome_mineral} por {valor} créditos!")
                            return valor
                        else:
                            print("⚠️ Erro ao vender mineral!")
                    else:
                        print(f"⚠️ Valor de mercado desconhecido para {nome_mineral}!")
                else:
                    print("⚠️ Quantidade inválida!")
            else:
                print("⚠️ Opção inválida!")
        except ValueError:
            print("⚠️ Por favor, digite um número válido!")

        time.sleep(1)
        return 0

    def comprar_upgrade(self, upgrade):
        requisitos = UPGRADES_DISPONIVEIS[upgrade]

        # Verifica créditos e recursos
        if (self.creditos < requisitos["creditos"] or
                any(self.mochila.conteudo.get(recurso, 0) < qtd
                    for recurso, qtd in requisitos["recursos"].items())):
            return False, "Recursos insuficientes"

        # Deduz custos
        self.creditos -= requisitos["creditos"]
        for recurso, qtd in requisitos["recursos"].items():
            self.mochila.remover_mineral(recurso, qtd)

        # Aplica upgrade
        self.nave.upgrades[upgrade] = True

        # Efeitos específicos
        if upgrade == "motor_fusao":
            self.nave.combustivel_max = 150
            self.nave.combustivel = min(self.nave.combustivel, 150)
            mensagem = "Motor de Dobra Nuclear instalado! Capacidade de combustível aumentada."

        elif upgrade == "escudo_antimat":
            self.nave.dano = max(0, self.nave.dano - 10)  # Repara 10% ao instalar
            mensagem = "Escudo de Antimatéria ativado! Nave reparada em 10%."

        elif upgrade == "traje_avancado":
            mensagem = "Traje Espacial equipado! Proteção contra vazamentos ativada."

        return True, mensagem

#---------------------------------------------------------------------------------------------

# Definição da lógica do jogo (2/3)
MINERAIS_DISPONIVEIS = [
    Mineral("Ferro", 35, "🔩"),
    Mineral("Silício", 40, "🔧"),
    Mineral("Titânio", 50, "💠"),
    Mineral("Hélio-3", 80, "⚡"),
    Mineral("Ouro", 150, "💰"),
    Mineral("Cobre", 30, "🔶"),
    Mineral("Platina", 200, "🔷"),
    Mineral("Iridício", 300, "🛡️"),
    Mineral("Matéria escura", 500, "⚫"),
    Mineral("Antimatéria", 750, "💥")
]

# Definição de upgrades
UPGRADES_DISPONIVEIS = {
    "motor_fusao": {
        "nome_exibicao": "⚛️ Motor de Dobra Nuclear",
        "creditos": 16000,
        "recursos": {"Hélio-3": 50},
        "descricao": "Permite viagens intergalácticas e aumenta tanque de combustível"
    },
    "escudo_antimat": {
        "nome_exibicao": "🛡️ Escudo de Antimatéria",
        "creditos": 12000,
        "recursos": {
            "Ouro": 20, "Silício": 20},
        "descricao": "Protege contra asteroides e reduz danos em 50%"
    },
    "traje_avancado": {
        "nome_exibicao": "👨‍🚀 Traje Espacial",
        "creditos": 8000,
        "recursos": {"Titânio": 20, "Cobre": 15},
        "descricao": "Previne perda de minérios em eventos de falha no traje"
    }
}

# Definição de planetas
PLANETAS_HELIOS_REACH = [
    Planeta(
        "Terra-10005",
        [next(m for m in MINERAIS_DISPONIVEIS if m.nome == "Ferro"),
         next(m for m in MINERAIS_DISPONIVEIS if m.nome == "Silício")],
        10,
        ["Falha no Traje"]  # Evento único
    ),
    Planeta(
        "Luna",
        [next(m for m in MINERAIS_DISPONIVEIS if m.nome == "Titânio"),
         next(m for m in MINERAIS_DISPONIVEIS if m.nome == "Hélio-3")],
        15,
        ["Vazamento de O₂"]  # Evento único
    ),
    Planeta(
        "Planeta Vermelho",
        [next(m for m in MINERAIS_DISPONIVEIS if m.nome == "Ouro"),
         next(m for m in MINERAIS_DISPONIVEIS if m.nome == "Cobre")],
        20,
        ["Areia Movediça"]  # Evento único
    ),
    Planeta(
        "Cinturão X-201",
        [next(m for m in MINERAIS_DISPONIVEIS if m.nome == "Platina"),
         next(m for m in MINERAIS_DISPONIVEIS if m.nome == "Iridício")],
        30,
        ["Asteroide Próximo"]  # Evento único
    )
]

PLANETAS_INTERGALACTICOS = [
    Planeta(
        "Andrômeda Prime",
        [next(m for m in MINERAIS_DISPONIVEIS if m.nome == "Matéria escura"),
         next(m for m in MINERAIS_DISPONIVEIS if m.nome == "Antimatéria")],
        50,
        ["Alienígenas negociantes"]  # Evento único
    )
]

def mostrar_status(jogador):
    os.system('cls' if os.name == 'nt' else 'clear')

    print("\n=== 🚀 STELLAR DRILLER ===")
    print(f"👨‍🚀 Comandante: {jogador.nome}")
    print(f"🌟 Nível: {jogador.nivel} | 🔷 Experiência: {jogador.experiencia}/100")
    print(f"💰 Créditos: {jogador.creditos}")
    print(f"⛽ Combustível: {int(jogador.nave.combustivel)}/{jogador.nave.combustivel_max}")
    print(f"⚡ Estado da Nave: {100 - jogador.nave.dano}%")

    # Mostra localização atual
    print(f"\n🌌 Localização: {jogador.localizacao}")
    if jogador.planeta_atual:
        print(f"🌍 Planeta Atual: {jogador.planeta_atual.nome}")
        if jogador.planeta_atual.evento_ativo:
            print(
                f"   ⚠️ Evento Ativo: {jogador.planeta_atual.evento_ativo} ({jogador.planeta_atual.tempo_evento}s restantes)")

        print("\n💎 Minérios disponíveis:")
        for mineral in jogador.planeta_atual.minerais:
            print(f"   {mineral.icon} {mineral.nome}: {jogador.planeta_atual.riqueza[mineral.nome]} unidades")
    else:
        print("\nVocê está no espaço profundo")


def mostrar_mochila(jogador):
    print("\n=== 🎒 MOCHILA ===")
    print(f"Espaço: {sum(jogador.mochila.conteudo.values())}/{jogador.mochila.capacidade}")
    print(f"💰 Valor estimado: {jogador.mochila.calcular_valor_total()} créditos")

    if not jogador.mochila.conteudo:
        print("\nA mochila está vazia")
        return

    print("\nConteúdo:")
    for mineral, qtd in jogador.mochila.conteudo.items():
        mineral_obj = next(m for m in MINERAIS_DISPONIVEIS if m.nome == mineral)
        print(f"   {mineral_obj.icon} {mineral}: {qtd} unidades")


def mostrar_upgrades(jogador):
    print("\n=== ⚙️ MELHORIAS DISPONÍVEIS ===")
    for upgrade_id, dados in UPGRADES_DISPONIVEIS.items():
        status = "✅" if jogador.nave.upgrades[upgrade_id] else "❌"
        print(f"\n{status} {dados['nome_exibicao']}")
        print(f"   Preço: {dados['creditos']} créditos")
        print(f"   Recursos: {', '.join([f'{qtd} {nome}' for nome, qtd in dados['recursos'].items()])}")
        print(f"   Efeito: {dados['descricao']}")


def mostrar_planetas_disponiveis(jogador):
    print("\n=== 🌠 PLANETAS DISPONÍVEIS ===")
    planetas_disponiveis = []

    # Planetas da Helios Reach (sempre visíveis)
    for i, planeta in enumerate(PLANETAS_HELIOS_REACH, start=1):
        planetas_disponiveis.append(planeta)
        custo = int(planeta.dificuldade / jogador.nave.velocidade)
        print(f"{i}. {planeta.nome} - ⛽ Custo: {custo}")
        if planeta.nome in jogador.planetais_visitados:
            minerais = [f"{m.icon} {m.nome}" for m in planeta.minerais]
            print(f"   Minérios: {' e '.join(minerais)}")

    # Planetas intergalácticos (requer motor de dobra)
    if jogador.nave.upgrades.get("motor_fusao", False):
        for j, planeta in enumerate(PLANETAS_INTERGALACTICOS, start=len(PLANETAS_HELIOS_REACH) + 1):
            if planeta.nome in jogador.planetais_descobertos:
                planetas_disponiveis.append(planeta)
                custo = int(planeta.dificuldade / jogador.nave.velocidade)
                print(f"{j}. {planeta.nome} - ⛽ Custo: {custo}")
                print(f"   Requisitos: 50 Hélio-3 para ignição do motor")
                if planeta.nome in jogador.planetais_visitados:
                    minerais = [f"{m.icon} {m.nome}" for m in planeta.minerais]
                    print(f"   Minérios: {' e '.join(minerais)}")

    return planetas_disponiveis


def menu_principal(jogador):
    print("\n📜 MENU PRINCIPAL")

    opcoes = []

    if jogador.planeta_atual:
        opcoes.append("1. Minerar")
        opcoes.append("2. Viajar para outro planeta")
    else:
        opcoes.append("1. Viajar para um planeta")
        opcoes.append("2. Estação espacial")  # Função nova para recarregar combustível
    opcoes.extend([
        "3. Ver mochila",
        "4. Vender minérios",
        "5. Melhorias",
        "6. Reparar nave",
        "7. Sair do jogo"
    ])

    print("\n".join(opcoes))
    return input("\nEscolha uma ação: ")


def carregar_jogo():
    try:
        with open('minerador_save.dat', 'rb') as f:
            return pickle.load(f)
    except:
        return None


def salvar_jogo(jogador):
    #Salva o progresso do jogador
    try:
        with open('minerador_save.dat', 'wb') as f:
            pickle.dump(jogador, f)
        return True
    except Exception as e:
        print(f"⚠️ Erro ao salvar jogo: {e}")
        return False

#---------------------------------------------------------------------------------------------

# Loop principal do jogo (3/3)

def main():
    # Inicialização do jogo
    jogador_salvo = carregar_jogo()
    if jogador_salvo:
        jogador = jogador_salvo
        print("🚀 Jogo carregado com sucesso.")
        print("👨‍🚀 Bem-vindo de volta, comandante!")
    else:
        nome = input("👨‍🚀 Digite seu nome, comandante: ")
        jogador = Jogador(nome)
        jogador.planetais_descobertos.update(p.nome for p in PLANETAS_HELIOS_REACH)
        print("\n🌌 Bem-vindo à Helios Reach,comandante!")
        print("Explore planetas, colete minérios e melhore sua nave.")
        print("Use os créditos para comprar melhorias e desbloquear novos setores da galáxia!")
        time.sleep(3)

    # Início do loop
    while True:
        mostrar_status(jogador)

        if jogador.planeta_atual:
            # Verifica se um novo evento deve ocorrer
            evento = jogador.planeta_atual.verificar_evento()
            if evento:
                print(f"\n⚠️ EVENTO: {evento}!")
                resultado = jogador.nave.aplicar_evento(evento, jogador)
                if resultado:
                    print(resultado)
                time.sleep(2)

            # Atualiza o contador do evento atual
            jogador.planeta_atual.atualizar_evento()

            if jogador.planeta_atual.nome == "Cinturão X-201":
                if random.random() < 0.25:  # 25% de chance
                    resultado = jogador.nave.aplicar_evento("Asteroide Próximo", jogador)
                    print(resultado)
                    time.sleep(2)

            def verificar_evento_especial_cinturao(jogador, chegada=True):
                if jogador.planeta_atual and jogador.planeta_atual.nome == "Cinturão X-201":
                    if random.random() < 0.25:  # 25% de chance
                        resultado = jogador.nave.aplicar_evento("Asteroide Próximo", jogador)
                        print(f"\n{'CHEGADA' if chegada else 'SAÍDA'} NO CINTURÃO X-201")
                        print(resultado)
                        time.sleep(2)

            # Chamar quando chegar:
            verificar_evento_especial_cinturao(jogador, chegada=True)

            # Chamar quando sair:
            verificar_evento_especial_cinturao(jogador, chegada=False)

        # Verifica se a nave foi destruída
        if jogador.nave.dano >= 100:
            # Mostra mensagem de game over
            print("\n\n💥 SUA NAVE FOI DESTRUÍDA! 💥")
            print("========================================")
            print("O asteroide reduziu seu veículo a escombros.")
            print("Seus minérios se perdem no vácuo do espaço...")
            print("Os sistemas de emergência falharam...")
            print("\n🚨 FIM DE JOGO 🚨")
            time.sleep(3)

            # Remove o arquivo de save para resetar o jogo
            import os
            save_file = 'minerador_save.dat'

            if os.path.exists(save_file):
                try:
                    os.remove(save_file)
                    print("\n⚙️ Arquivo de progresso foi resetado.")
                except Exception as e:
                    print(f"\n⚠️ Não foi possível resetar o save: {e}")

            time.sleep(2)
            exit(1)  # Encerra o jogo com código de erro

        escolha = menu_principal(jogador)

        if escolha == "1":  # Minerar ou Viajar
            if jogador.planeta_atual:  # Minerar
                print("\n💎 Minérios disponíveis:")
                for i, mineral in enumerate(jogador.planeta_atual.minerais):
                    print(f"{i + 1}. {mineral.icon} {mineral.nome}")

                try:
                    opcao = int(input("Escolha o minério para minerar: ")) - 1
                    if 0 <= opcao < len(jogador.planeta_atual.minerais):
                        mineral = jogador.planeta_atual.minerais[opcao]
                        minerado = jogador.nave.minerar(jogador.planeta_atual, mineral)

                        if minerado > 0:
                            if jogador.mochila.adicionar_mineral(mineral, minerado):

                                experiencia_ganha = minerado * 3  # 3x mais experiência que antes, para melhor progresso
                                if jogador.ganhar_experiencia(experiencia_ganha):
                                    print(f"🎉 Subiu para o nível {jogador.nivel}!")
                            else:
                                print("⚠️ Mochila cheia! Venda ou descarte alguns itens.")
                        else:
                            print("⚠️ Falha na mineração")
                    else:
                        print("⚠️ Opção inválida!")
                except ValueError:
                    print("⚠️ Por favor, digite um número válido!")
                time.sleep(2)


            else:  # Viajar

                mostrar_planetas_disponiveis(jogador)

                try:

                    opcao = int(input("\nEscolha um planeta para viajar (0 para cancelar): "))

                    if opcao == 0:
                        continue

                    planetas_disponiveis = []

                    if jogador.localizacao == "Helios Reach":

                        planetas_disponiveis.extend(PLANETAS_HELIOS_REACH)

                        # Verifica se Andrômeda já foi descoberta

                        if "Andrômeda Prime" in jogador.planetais_descobertos:
                            planetas_disponiveis.extend(PLANETAS_INTERGALACTICOS)

                    else:

                        planetas_disponiveis.extend(PLANETAS_INTERGALACTICOS)

                    if 1 <= opcao <= len(planetas_disponiveis):

                        planeta = planetas_disponiveis[opcao - 1]

                        if planeta.nome == "Andrômeda Prime":
                            # Primeiro verifica todos os requisitos ANTES de atualizar a localização
                            if not jogador.nave.upgrades.get("motor_fusao"):
                                print("⚠️ Você precisa do Motor de Fusão para viajar para Andrômeda!")
                                time.sleep(2)
                                continue

                            helio3 = jogador.mochila.conteudo.get("Hélio-3", 0)
                            if helio3 < 50:
                                print("⚠️ Você precisa de 50 Hélio-3 para a ignição do motor!")
                                time.sleep(2)
                                continue

                            # Só atualiza a localização SE todos os requisitos forem atendidos
                            jogador.localizacao = "Galáxia de Andrômeda"
                            jogador.mochila.conteudo["Hélio-3"] = helio3 - 50
                            print("⚛️ 50 Hélio-3 consumidos para ignição do motor de dobra!")

                        custo = planeta.dificuldade / jogador.nave.velocidade

                        if jogador.nave.viajar(custo):

                            jogador.planeta_atual = planeta

                            jogador.planetais_visitados.add(planeta.nome)

                            print(f"🛸 Você chegou em {planeta.nome}!")

                            if planeta.nome == "Cinturão X-201" and "Andrômeda Prime" not in jogador.planetais_descobertos:
                                andromeda = next(p for p in PLANETAS_INTERGALACTICOS if p.nome == "Andrômeda Prime")

                                jogador.planetais_descobertos.add(andromeda.nome)

                                print("\n┏" + "━" * 38 + "┓")

                                print("┃  🌟 DESCOBERTA: ANDRÔMEDA PRIME  ┃")

                                print("┗" + "━" * 38 + "┛")

                                print("\nSeus sensores detectaram uma anomalia no cinturão:")

                                print(f"- Portal estável para {andromeda.nome}")

                                print(f"- Coordenadas: X-{random.randint(100, 999)}Y-{random.randint(100, 999)}")

                                print("\n⚡ Requisitos:")

                                print(f"✔ Motor de Dobra ({andromeda.dificuldade} combustível)")

                                print(f"✔ 50 Hélio-3 para ignição")

                                print("\nTransmissão interceptada: \"...roteiro seguro... comerciantes aguardam...\"")

                                print("\n[Enter] para registrar descoberta")

                                input()

                                print(f"✓ {andromeda.nome} disponível para viagem!")

                                time.sleep(2)



                        else:

                            # Cena de game over quando fica sem combustível

                            print("\n⚠️ Combustível insuficiente para viajar!")

                            time.sleep(2)

                            print("\n\n===========================================")

                            print("  VOCÊ FICOU PRESO NA DERIVA DO ESPAÇO...")

                            print("===========================================")

                            print("\n* Sem combustível, sua nave perde comunicação e energia.")

                            print("* Os minérios coletados flutuam no vácuo, inalcançáveis.")

                            print("* Os alienígenas da Estação Forja Estelar registram seu último sinal:")

                            print("  'Sinal perdido: mais um humano vira estátua de metal no cosmos.'")

                            print("\n💀 FIM DE JOGO 💀")

                            # Deleta o save game

                            import os

                            save_file = 'minerador_save.dat'

                            if os.path.exists(save_file):

                                try:

                                    os.remove(save_file)

                                    print("\n⚙️ Arquivo de progresso foi resetado.")

                                except Exception as e:

                                    print(f"\n⚠️ Não foi possível resetar o save: {e}")

                            time.sleep(3)

                            exit(1)

                    else:

                        print("⚠️ Planeta inválido!")

                except ValueError:

                    print("⚠️ Por favor, digite um número válido!")

                time.sleep(2)



        elif escolha == "2":

            if jogador.planeta_atual:  # Se está em um planeta

                jogador.planeta_atual = None

                print("🚀 Você decolou para o espaço profundo")

                time.sleep(1)

            else:  # Se já está no espaço

                # Menu da Estação Espacial

                print("\n*Docking na Estação Forja Estelar...*")

                print("\"Salve, humano! Recarrego combustível por créditos. De quanto precisa?\"")

                while True:

                    print(f"\n💰 Seus créditos: {jogador.creditos}")

                    print(f"🔋 Combustível atual: {int(jogador.nave.combustivel)}/{jogador.nave.combustivel_max}")

                    print("\n1. Recarregar 100% combustível (5000 Créditos)")

                    print("2. Recarregar 20% combustível (1000 Créditos)")

                    print("3. Sair da estação")

                    opcao_estacao = input("\nEscolha: ").strip()

                    if opcao_estacao == "1":

                        if jogador.creditos >= 5000:

                            jogador.creditos -= 5000

                            jogador.nave.combustivel = jogador.nave.combustivel_max

                            print(f"\n🔋 Combustível recarregado para 100%! (-5000 créditos)")

                            print(f"💰 Créditos restantes: {jogador.creditos}")

                        else:

                            print(f"\n⚠️ Você precisa de 5000 créditos (você tem: {jogador.creditos})")

                        time.sleep(1.5)


                    elif opcao_estacao == "2":

                        if jogador.creditos >= 1000:

                            jogador.creditos -= 1000

                            recarga = jogador.nave.combustivel_max * 0.2

                            jogador.nave.combustivel = min(jogador.nave.combustivel + recarga,

                                                           jogador.nave.combustivel_max)

                            print(f"\n🔋 Combustível recarregado em 20%! (-1000 créditos)")

                            print(f"💰 Créditos restantes: {jogador.creditos}")

                        else:

                            print(f"\n⚠️ Você precisa de 1000 créditos (você tem: {jogador.creditos})")

                        time.sleep(1.5)


                    elif opcao_estacao == "3":

                        print("\n*Desacoplando da estação...*")

                        time.sleep(1)

                        break


                    else:

                        print("\nOpção inválida!")

                        time.sleep(1)

        elif escolha == "3":  # Ver mochila
            while True:
                mostrar_mochila(jogador)
                print("\n1. Voltar")
                print("2. Descartar minérios")

                opcao = input("Escolha uma ação: ")
                if opcao == "1":
                    break
                elif opcao == "2":
                    if not jogador.mochila.conteudo:
                        print("⚠️ Mochila vazia!")
                        time.sleep(1)
                        continue

                    print("\nMinérios disponíveis para descarte:")
                    minerais = list(jogador.mochila.conteudo.items())
                    for i, (mineral, qtd) in enumerate(minerais):
                        print(f"{i + 1}. {mineral}: {qtd} unidades")

                    try:
                        opcao_min = int(input("Escolha o minério para descartar (0 para cancelar): ")) - 1
                        if opcao_min == -1:
                            continue

                        if 0 <= opcao_min < len(minerais):
                            mineral, qtd = minerais[opcao_min]
                            qtd_descartar = int(input(f"Quantidade de {mineral} para descartar (max {qtd}): "))
                            if 0 < qtd_descartar <= qtd:
                                jogador.mochila.remover_mineral(mineral, qtd_descartar)
                                print(f"🗑️ Descartou {qtd_descartar} unidades de {mineral}")
                            else:
                                print("⚠️ Quantidade inválida!")
                        else:
                            print("⚠️ Opção inválida!")
                    except ValueError:
                        print("⚠️ Por favor, digite um número válido!")
                    time.sleep(1)
                else:
                    print("⚠️ Opção inválida!")
                    time.sleep(1)

        elif escolha == "4":  # Vender minérios
            valor = jogador.vender_minerais()
            if valor > 0:
                print(f"💰 Você vendeu minérios por {valor} créditos!")
            else:
                print("⚠️ Nenhum minério para vender!")
            time.sleep(2)


        elif escolha == "5":  # Melhorias

            while True:

                mostrar_upgrades(jogador)

                print("\n1. Voltar")

                print("2. Comprar melhoria")

                opcao = input("Escolha uma ação: ")

                if opcao == "1":

                    break

                elif opcao == "2":

                    upgrades_disponiveis = [up for up in UPGRADES_DISPONIVEIS if not jogador.nave.upgrades[up]]

                    if not upgrades_disponiveis:
                        print("⚠️ Todos os upgrades já foram comprados!")

                        time.sleep(1)

                        continue

                    print("\nMelhorias disponíveis para compra:")

                    for i, upgrade_id in enumerate(upgrades_disponiveis, 1):
                        dados_upgrade = UPGRADES_DISPONIVEIS[upgrade_id]

                        print(f"{i}. {dados_upgrade['nome_exibicao']} - {dados_upgrade['creditos']} créditos")

                    try:

                        opcao_up = int(input("Escolha o upgrade para comprar (0 para cancelar): ")) - 1

                        if opcao_up == -1:
                            continue

                        if 0 <= opcao_up < len(upgrades_disponiveis):

                            upgrade_id = upgrades_disponiveis[opcao_up]

                            sucesso, mensagem = jogador.comprar_upgrade(upgrade_id)

                            print(mensagem)

                        else:

                            print("⚠️ Opção inválida!")

                    except ValueError:

                        print("⚠️ Por favor, digite um número válido!")

                    time.sleep(2)

        elif escolha == "6":  # Reparar nave
            custo = jogador.nave.dano * 50
            print(f"\n⚡ Estado da nave: {100 - jogador.nave.dano}%")
            print(f"🔧 Custo para reparos: {custo} créditos")

            if jogador.nave.dano == 0:
                print("✅ Sua nave já está em perfeito estado!")
                time.sleep(1)
                continue

            confirmar = input(f"Deseja reparar sua nave por {custo} créditos? (s/n): ").lower()
            if confirmar == 's':
                if jogador.creditos >= custo:
                    jogador.creditos -= custo
                    jogador.nave.dano = 0
                    print("🔧 Nave totalmente reparada!")
                else:
                    print("⚠️ Créditos insuficientes!")
            time.sleep(2)

        elif escolha == "7":  # Sair
            salvar_jogo(jogador)
            print("🚀 Progresso salvo. Até a próxima, comandante!")
            break

        else:
            print("⚠️ Opção inválida!")
            time.sleep(1)


if __name__ == "__main__":
    main()
