import time
import os
import random
import pickle
from enum import Enum


class TipoMineral(Enum):
    COMERCIAL = 1
    TECNICO = 2


class Mineral:
    def __init__(self, nome, tipo, valor, icon):
        self.nome = nome
        self.tipo = tipo
        self.valor = valor
        self.icon = icon


class Planeta:
    def __init__(self, nome, minerais, dificuldade, eventos):
        self.nome = nome
        self.minerais = minerais  # Lista de minerais disponíveis
        self.dificuldade = dificuldade
        self.eventos = eventos
        self.riqueza = {mineral.nome: random.randint(50, 150) for mineral in minerais}
        self.evento_ativo = None
        self.tempo_evento = 0

    def minerar(self, mineral_alvo):
        if self.riqueza[mineral_alvo.nome] <= 0:
            return 0

        base_minerado = random.randint(3, 8)

        # Aplica efeito de evento
        if self.evento_ativo == "Tempestade de areia":
            base_minerado = int(base_minerado * 0.7)
        elif self.evento_ativo == "Distorção temporal":
            base_minerado = base_minerado * 2

        minerado = min(base_minerado, self.riqueza[mineral_alvo.nome])
        self.riqueza[mineral_alvo.nome] -= minerado
        return minerado

    def verificar_evento(self):
        # 20% de chance de um evento ocorrer
        if random.random() < 0.2 and not self.evento_ativo:
            self.evento_ativo = random.choice(self.eventos)
            self.tempo_evento = 30  # 30 segundos
            return self.evento_ativo
        return None

    def atualizar_evento(self):
        if self.evento_ativo and self.tempo_evento > 0:
            self.tempo_evento -= 1
            if self.tempo_evento <= 0:
                self.evento_ativo = None


class Mochila:
    def __init__(self, capacidade=50):
        self.capacidade = capacidade
        self.conteudo = {}
        self.creditos_estimados = 0

    def adicionar_mineral(self, mineral, quantidade):
        if self.espaco_disponivel() >= quantidade:
            if mineral.nome in self.conteudo:
                self.conteudo[mineral.nome] += quantidade
            else:
                self.conteudo[mineral.nome] = quantidade

            if mineral.tipo == TipoMineral.COMERCIAL:
                self.creditos_estimados += quantidade * mineral.valor
            return True
        return False

    def remover_mineral(self, mineral_nome, quantidade):
        if mineral_nome in self.conteudo and self.conteudo[mineral_nome] >= quantidade:
            self.conteudo[mineral_nome] -= quantidade

            # Atualiza créditos estimados se for mineral comercial
            for mineral in MINERAIS_DISPONIVEIS:
                if mineral.nome == mineral_nome and mineral.tipo == TipoMineral.COMERCIAL:
                    self.creditos_estimados -= quantidade * mineral.valor
                    break

            if self.conteudo[mineral_nome] == 0:
                del self.conteudo[mineral_nome]
            return True
        return False

    def espaco_disponivel(self):
        return self.capacidade - sum(self.conteudo.values())

    def calcular_valor_total(self):
        total = 0
        for nome, qtd in self.conteudo.items():
            mineral = next(m for m in MINERAIS_DISPONIVEIS if m.nome == nome)
            if mineral.tipo == TipoMineral.COMERCIAL:
                total += qtd * mineral.valor
        return total


class Nave:
    def __init__(self):
        self.combustivel = 100
        self.combustivel_max = 100
        self.velocidade = 1
        self.capacidade_mineracao = 1
        self.dano = 0  # 0-100, se chegar a 100 a nave é destruída
        self.upgrades = {
            "motor_fusao": True,
            "escudo_antimat": False
        }

    def viajar(self, custo):
        custo_ajustado = custo / self.velocidade
        if self.combustivel >= custo_ajustado:
            self.combustivel -= custo_ajustado
            return True
        return False

    def minerar(self, planeta, mineral):
        custo = planeta.dificuldade * 0.5
        if self.combustivel >= custo:
            minerado = planeta.minerar(mineral)
            if minerado > 0:
                self.combustivel -= custo
                return int(minerado * self.capacidade_mineracao)
        return 0

    def reparar(self, quantidade):
        self.dano = max(0, self.dano - quantidade)

    def aplicar_evento(self, evento, jogador):  # Adicione 'jogador' como parâmetro
        if evento == "Vazamento de O₂" and "Hélio-3" in jogador.mochila.conteudo:
            qtd_perdida = int(jogador.mochila.conteudo["Hélio-3"] * 0.1)
            jogador.mochila.remover_mineral("Hélio-3", qtd_perdida)
            return f"⚠️ Perdeu {qtd_perdida} Hélio-3 no vazamento!"

        elif evento == "Asteroide próximo":
            if self.upgrades["escudo_antimat"]:
                return "🛡️ Seus escudos avançados protegeram a nave do asteroide!"
            else:
                self.dano += 20
                return "💥 Asteroide atingiu sua nave! +20% de dano"

        elif evento == "Falha na Nave":
            if jogador.creditos >= 2000:
                jogador.creditos -= 2000
                return "🔧 Você pagou 2.000 créditos para reparar a falha"
            else:
                if jogador.mochila.conteudo:
                    mineral_perdido = random.choice(list(jogador.mochila.conteudo.keys()))
                    jogador.mochila.remover_mineral(mineral_perdido, 1)
                    return f"⚠️ Perdeu 1 unidade de {mineral_perdido} devido à falha"
                else:
                    self.dano += 10
                    return "⚠️ Falha crítica! +10% de dano na nave"

        return None


class Jogador:
    def __init__(self, nome):
        self.nome = nome
        self.nave = Nave()
        self.mochila = Mochila()
        self.creditos = 5000  # Começa com mais créditos para testes
        self.experiencia = 0
        self.nivel = 1
        self.localizacao = "Via Láctea"
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
        total = self.mochila.calcular_valor_total()
        minerais_vendidos = [m for m in self.mochila.conteudo.items()
                             if next((min for min in MINERAIS_DISPONIVEIS
                                      if min.nome == m[0] and min.tipo == TipoMineral.COMERCIAL), None)]

        for mineral, qtd in minerais_vendidos:
            self.mochila.remover_mineral(mineral, qtd)

        self.creditos += total
        return total

    def comprar_upgrade(self, upgrade):
        requisitos = UPGRADES_DISPONIVEIS[upgrade]

        # Verifica créditos
        if self.creditos < requisitos["creditos"]:
            return False, "Créditos insuficientes"

        # Verifica recursos
        for recurso, qtd in requisitos["recursos"].items():
            if self.mochila.conteudo.get(recurso, 0) < qtd:
                return False, f"Recurso insuficiente: {recurso}"

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
        elif upgrade == "broca_laser":
            self.nave.capacidade_mineracao = 1.5

        return True, "Upgrade instalado com sucesso!"


# Definição de minerais disponíveis
MINERAIS_DISPONIVEIS = [
    Mineral("Ferro", TipoMineral.COMERCIAL, 10, "💰"),
    Mineral("Silício", TipoMineral.TECNICO, 0, "🔧"),
    Mineral("Titânio", TipoMineral.COMERCIAL, 25, "💰"),
    Mineral("Hélio-3", TipoMineral.TECNICO, 0, "🚀"),
    Mineral("Ouro", TipoMineral.COMERCIAL, 50, "💰"),
    Mineral("Cobre", TipoMineral.TECNICO, 0, "🔧"),
    Mineral("Platina", TipoMineral.COMERCIAL, 100, "💰"),
    Mineral("Iridício", TipoMineral.TECNICO, 0, "🛡️"),
    Mineral("Dark Matter", TipoMineral.COMERCIAL, 300, "💰"),
    Mineral("Antimatéria", TipoMineral.TECNICO, 0, "💥")
]

# Definição de upgrades
UPGRADES_DISPONIVEIS = {
    "motor_fusao": {
        "nome_exibicao": "⚛️ Motor de Dobra Nuclear",  # Novo campo adicionado
        "creditos": 10000,
        "recursos": {"Hélio-3": 50},
        "descricao": "Permite viagens intergalácticas"  # Descrição original mantida
    },
    "escudo_antimat": {
        "nome_exibicao": "✨ Escudo de Antimatéria",  # Novo campo adicionado
        "creditos": 25000,
        "recursos": {"Dark Matter": 20},
        "descricao": "Protege contra asteroides"  # Descrição original mantida
    }
}

# Definição de planetas
PLANETAS_VIA_LACTEA = [
    Planeta(
        "Terra-616",
        [next(m for m in MINERAIS_DISPONIVEIS if m.nome == "Ferro"),
         next(m for m in MINERAIS_DISPONIVEIS if m.nome == "Silício")],
        10,
        ["Tempestade de areia", "Falha na Nave"]
    ),
    Planeta(
        "Luna-3",
        [next(m for m in MINERAIS_DISPONIVEIS if m.nome == "Titânio"),
         next(m for m in MINERAIS_DISPONIVEIS if m.nome == "Hélio-3")],
        15,
        ["Vazamento de O₂", "Geiseres de Europa"]
    ),
    Planeta(
        "Marte Vermelho",
        [next(m for m in MINERAIS_DISPONIVEIS if m.nome == "Ouro"),
         next(m for m in MINERAIS_DISPONIVEIS if m.nome == "Cobre")],
        20,
        ["Robôs marcianos", "Falha na Nave"]
    ),
    Planeta(
        "Cinturão X-201",
        [next(m for m in MINERAIS_DISPONIVEIS if m.nome == "Platina"),
         next(m for m in MINERAIS_DISPONIVEIS if m.nome == "Iridício")],
        30,
        ["Asteroide próximo", "Meteorito Precioso"]
    )
]

PLANETAS_INTERGALACTICOS = [
    Planeta(
        "Andrômeda Prime",
        [next(m for m in MINERAIS_DISPONIVEIS if m.nome == "Dark Matter"),
         next(m for m in MINERAIS_DISPONIVEIS if m.nome == "Antimatéria")],
        50,
        ["Alienígenas negociantes", "Distorção temporal"]
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
    for upgrade, dados in UPGRADES_DISPONIVEIS.items():
        status = "✅" if jogador.nave.upgrades[upgrade] else "❌"
        # Usa nome_exibicao se existir, caso contrário usa a chave do dicionário
        nome = dados.get("nome_exibicao", upgrade.replace('_', ' ').title())
        print(f"\n{status} {nome}")
        print(f"   Preço: {dados['creditos']} créditos")
        print(f"   Recursos: {', '.join([f'{qtd} {nome}' for nome, qtd in dados['recursos'].items()])}")
        print(f"   Efeito: {dados['descricao']}")


def mostrar_planetas_disponiveis(jogador):
    print("\n=== 🌠 PLANETAS DISPONÍVEIS ===")

    # Determina se estamos na Via Láctea ou em outra galáxia
    if jogador.localizacao == "Via Láctea":
        planetas_base = PLANETAS_VIA_LACTEA
        planetas_especiais = [p for p in PLANETAS_INTERGALACTICOS
                              if p.nome in jogador.planetais_descobertos and
                              jogador.nave.upgrades.get("motor_fusao", True)]
        planetas = planetas_base + planetas_especiais
    else:
        planetas = PLANETAS_INTERGALACTICOS

    # Mostra todos os planetas disponíveis
    for i, planeta in enumerate(planetas, start=1):
        custo = int(planeta.dificuldade / jogador.nave.velocidade)
        print(f"{i}. {planeta.nome} - ⛽ Custo: {custo}")

        if planeta.nome in jogador.planetais_visitados:
            minerais = [f"{m.icon} {m.nome}" for m in planeta.minerais]
            print(f"   Minérios: {' e '.join(minerais)}")

    # Mensagem sobre destinos bloqueados
    if (jogador.localizacao == "Via Láctea" and
            any(p.nome in jogador.planetais_descobertos and
                not jogador.nave.upgrades.get("motor_fusao", False)
                for p in PLANETAS_INTERGALACTICOS)):
        print("\nℹ️ Você tem destinos descobertos que precisam do Motor de Dobra!")


def menu_principal(jogador):
    print("\n📜 MENU PRINCIPAL")

    opcoes = []

    if jogador.planeta_atual:
        opcoes.append("1. Minerar")
        opcoes.append("2. Viajar para outro planeta")
    else:
        opcoes.append("1. Viajar para um planeta")

    opcoes.extend([
        "3. Ver mochila",
        "4. Vender minérios comerciais",
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
    with open('minerador_save.dat', 'wb') as f:
        pickle.dump(jogador, f)


def main():
    # Inicialização do jogo
    jogador_salvo = carregar_jogo()
    if jogador_salvo:
        jogador = jogador_salvo
        print("🚀 Jogo carregado com sucesso!")
    else:
        nome = input("👨‍🚀 Digite seu nome, comandante: ")
        jogador = Jogador(nome)
        jogador.planetais_descobertos.update(p.nome for p in PLANETAS_VIA_LACTEA)
        print("\n🌌 Bem-vindo à Via Láctea, Comandante!")
        print("Explore planetas, colete minérios e melhore sua nave.")
        print("Use os créditos para comprar melhorias e desbloquear novos setores da galáxia!")
        time.sleep(3)

    # Loop principal do jogo
    while True:
        mostrar_status(jogador)

        # Verifica eventos no planeta atual
        if jogador.planeta_atual:
            evento = jogador.planeta_atual.verificar_evento()
            if evento:
                print(f"\n⚠️ EVENTO: {evento}!")
                resultado = jogador.nave.aplicar_evento(evento)
                if resultado:
                    print(resultado)
                time.sleep(2)

            jogador.planeta_atual.atualizar_evento()

        # Verifica se a nave foi destruída
        if jogador.nave.dano >= 100:
            print("\n💥 SUA NAVE FOI DESTRUÍDA!")
            print("Você perdeu todos os minérios e 50% dos créditos.")
            jogador.mochila = Mochila()
            jogador.creditos = int(jogador.creditos * 0.5)
            jogador.nave.dano = 0
            jogador.planeta_atual = None
            jogador.localizacao = "Via Láctea"
            time.sleep(3)
            continue

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
                                print(f"⛏️ Você minerou {minerado} unidades de {mineral.nome}!")
                                if jogador.ganhar_experiencia(minerado):
                                    print(f"🎉 Subiu para o nível {jogador.nivel}!")
                            else:
                                print("⚠️ Mochila cheia! Venda ou descarte alguns itens.")
                        else:
                            print("⚠️ Falha na mineração (sem combustível ou recursos esgotados)")
                    else:
                        print("⚠️ Opção inválida!")
                except ValueError:
                    print("⚠️ Por favor, digite um número válido!")
                time.sleep(2)

            else:  # Viajar
                mostrar_planetas_disponiveis(jogador)

                try:
                    opcao = int(input("\nEscolha um planeta para viajar (0 para cancelar): ")) - 1
                    if opcao == -1:
                        continue

                    if jogador.localizacao == "Via Láctea":
                        planetas = PLANETAS_VIA_LACTEA
                    else:
                        planetas = PLANETAS_INTERGALACTICOS

                    if 0 <= opcao < len(planetas):
                        planeta = planetas[opcao]

                        # Verifica se precisa de motor de dobra para planetas intergalácticos
                        if jogador.localizacao != "Via Láctea" and not jogador.nave.upgrades["motor_fusao"]:
                            print("⚠️ Você precisa do Motor de Fusão para viajar entre galáxias!")
                            time.sleep(2)
                            continue

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
                            print("⚠️ Combustível insuficiente para viajar!")
                    else:
                        print("⚠️ Planeta inválido!")
                except ValueError:
                    print("⚠️ Por favor, digite um número válido!")
                time.sleep(2)

        elif escolha == "2" and jogador.planeta_atual:  # Viajar para outro planeta
            jogador.planeta_atual = None
            print("🚀 Você decolou para o espaço profundo")
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
                print("⚠️ Nenhum minério comercial para vender!")
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

                    print("\nUpgrades disponíveis para compra:")
                    for i, upgrade in enumerate(upgrades_disponiveis):
                        print(f"{i + 1}. {upgrade.replace('_', ' ').title()}")

                    try:
                        opcao_up = int(input("Escolha o upgrade para comprar (0 para cancelar): ")) - 1
                        if opcao_up == -1:
                            continue

                        if 0 <= opcao_up < len(upgrades_disponiveis):
                            upgrade = upgrades_disponiveis[opcao_up]
                            sucesso, mensagem = jogador.comprar_upgrade(upgrade)
                            print(mensagem)

                            # Se comprou motor de fusão, pode viajar para outras galáxias
                            if sucesso and upgrade == "motor_fusao":
                                jogador.localizacao = "Andrômeda"
                                print("🌠 Motor de Fusão instalado! Agora você pode viajar para outras galáxias!")
                        else:
                            print("⚠️ Opção inválida!")
                    except ValueError:
                        print("⚠️ Por favor, digite um número válido!")
                    time.sleep(2)
                else:
                    print("⚠️ Opção inválida!")
                    time.sleep(1)

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
            print("🚀 Progresso salvo. Até a próxima, Comandante!")
            break

        else:
            print("⚠️ Opção inválida!")
            time.sleep(1)


if __name__ == "__main__":
    main()