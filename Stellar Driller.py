import time
import os
import random
import pickle
from enum import Enum

class TipoMineral(Enum):
    COMERCIAL = 1
    TECNICO = 2

class Mineral:
    def __init__(self, nome, tipo, valor, icon, desgaste):
        self.nome = nome
        self.tipo = tipo
        self.valor = valor
        self.icon = icon
        self.desgaste = desgaste

class Planeta:
    def __init__(self, nome, minerais, dificuldade, eventos):
        self.nome = nome
        self.minerais = minerais
        self.dificuldade = dificuldade
        self.eventos = eventos
        self.riqueza = {mineral.nome: random.randint(50, 150) for mineral in minerais}
        self.evento_ativo = None
        self.tempo_evento = 0

    def minerar(self, mineral_alvo):
        if self.riqueza[mineral_alvo.nome] <= 0:
            return 0
            
        base_minerado = random.randint(3, 8)
        
        if self.evento_ativo == "Tempestade de areia":
            base_minerado = int(base_minerado * 0.7)
        elif self.evento_ativo == "Distorção temporal":
            base_minerado = base_minerado * 2
            
        minerado = min(base_minerado, self.riqueza[mineral_alvo.nome])
        self.riqueza[mineral_alvo.nome] -= minerado
        return minerado

    def verificar_evento(self):
        if random.random() < 0.2 and not self.evento_ativo:
            self.evento_ativo = random.choice(self.eventos)
            self.tempo_evento = 30
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
        self.dano = 0
        self.broca_durabilidade = 100
        self.broca_durabilidade_max = 100
        self.upgrades = {
            "motor_fusao": False,
            "escudo_antimat": False,
            "broca_laser": False,
            "broca_reforcada": False,
            "broca_diamantada": False
        }

    def viajar(self, custo):
        custo_ajustado = custo / self.velocidade
        if self.combustivel >= custo_ajustado:
            self.combustivel -= custo_ajustado
            return True
        return False

    def minerar(self, planeta, mineral):
        eficiencia = self.capacidade_mineracao
        if self.broca_durabilidade <= 0:
            eficiencia *= 0.5
            
        if self.upgrades["broca_laser"]:
            eficiencia *= 1.5
        if self.upgrades["broca_diamantada"]:
            eficiencia *= 2.0
            
        custo = planeta.dificuldade * 0.5
        if self.combustivel >= custo:
            minerado = int(planeta.minerar(mineral) * eficiencia)
            self.combustivel -= custo
            
            if not self.upgrades["broca_diamantada"]:
                self.broca_durabilidade -= mineral.desgaste
                if self.broca_durabilidade < 0:
                    self.broca_durabilidade = 0
            
            return int(minerado)
        return 0
    
        def reparar(self, quantidade):
        self.dano = max(0, self.dano - quantidade)

    def reparar_broca(self, quantidade, usar_recursos=False, jogador=None):
        custo = 0
        recursos_necessarios = {}
        
        if quantidade == 100:
            custo = 800
            recursos_necessarios = {"Cobre": 2}
        else:
            custo = 500
            recursos_necessarios = {"Cobre": 1}
        
        if usar_recursos:
            for recurso, qtd in recursos_necessarios.items():
                if jogador.mochila.conteudo.get(recurso, 0) < qtd:
                    return False, f"Recursos insuficientes (falta {recurso})"
            
            for recurso, qtd in recursos_necessarios.items():
                jogador.mochila.remover_mineral(recurso, qtd)
            self.broca_durabilidade = min(self.broca_durabilidade_max, self.broca_durabilidade + quantidade)
            return True, "Broca reparada com recursos!"
        else:
            if jogador.creditos >= custo:
                jogador.creditos -= custo
                self.broca_durabilidade = min(self.broca_durabilidade_max, self.broca_durabilidade + quantidade)
                return True, f"Broca reparada por {custo} créditos!"
            else:
                return False, f"Créditos insuficientes ({custo} necessários)"

    def aplicar_evento(self, evento):
        if evento == "Vazamento de O₂" and "Hélio-3" in jogador.mochila.conteudo:
            qtd_perdida = int(jogador.mochila.conteudo["Hélio-3"] * 0.1)
            jogador.mochila.remover_mineral("Hélio-3", qtd_perdida)
            return f"⚠️ Perdeu {qtd_perdida} Hélio-3 no vazamento!"
        elif evento == "Asteroide próximo":
            if self.upgrades["escudo_antimat"]:
                return "🛡️ Seus escudos protegeram a nave!"
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
                    return f"⚠️ Perdeu 1 unidade de {mineral_perdido}"
                else:
                    self.dano += 10
                    return "⚠️ Falha crítica! +10% de dano"
        elif evento == "Geiseres de Europa":
            self.reparar(15)
            return "💧 Água mineral reparou 15% da nave!"
        elif evento == "Robôs marcianos":
            if self.broca_durabilidade < 30:
                self.broca_durabilidade -= 20
                if self.broca_durabilidade < 0:
                    self.broca_durabilidade = 0
                return "🤖 Robôs sabotaram sua broca! -20 de durabilidade"
            elif self.broca_durabilidade > 70:
                self.broca_durabilidade += 10
                if self.broca_durabilidade > self.broca_durabilidade_max:
                    self.broca_durabilidade = self.broca_durabilidade_max
                return "🤖 Robôs ajudaram a reparar sua broca! +10 de durabilidade"
            else:
                return "🤖 Robôs marcianos observam seu trabalho..."
        return None

class Jogador:
    def __init__(self, nome):
        self.nome = nome
        self.nave = Nave()
        self.mochila = Mochila()
        self.creditos = 5000
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
        
        if self.creditos < requisitos["creditos"]:
            return False, "Créditos insuficientes"
        
        for recurso, qtd in requisitos["recursos"].items():
            if self.mochila.conteudo.get(recurso, 0) < qtd:
                return False, f"Recurso insuficiente: {recurso}"
        
        self.creditos -= requisitos["creditos"]
        for recurso, qtd in requisitos["recursos"].items():
            self.mochila.remover_mineral(recurso, qtd)
        
        self.nave.upgrades[upgrade] = True
        
        if upgrade == "motor_fusao":
            self.nave.combustivel_max = 150
            self.nave.combustivel = min(self.nave.combustivel, 150)
        elif upgrade == "broca_reforcada":
            self.nave.broca_durabilidade_max = 150
            self.nave.broca_durabilidade = 150
        elif upgrade == "broca_diamantada":
            self.nave.broca_durabilidade_max = 9999
            self.nave.broca_durabilidade = 9999
        
        return True, "Upgrade instalado com sucesso!"

    def comprar_combustivel(self, quantidade):
        custo = 0
        if quantidade == 50:
            custo = 1000
        elif quantidade == 100:
            custo = 1500
        
        if self.creditos >= custo:
            self.creditos -= custo
            self.nave.combustivel = min(self.nave.combustivel_max, self.nave.combustivel + quantidade)
            return True, f"⛽ Adicionado {quantidade} de combustível!"
        return False, "Créditos insuficientes"
    
    # Definição de minerais disponíveis
MINERAIS_DISPONIVEIS = [
    Mineral("Ferro", TipoMineral.COMERCIAL, 10, "💰", 3),
    Mineral("Silício", TipoMineral.TECNICO, 0, "🔧", 4),
    Mineral("Titânio", TipoMineral.COMERCIAL, 25, "💰", 5),
    Mineral("Hélio-3", TipoMineral.TECNICO, 0, "🚀", 15),
    Mineral("Ouro", TipoMineral.COMERCIAL, 50, "💰", 10),
    Mineral("Cobre", TipoMineral.TECNICO, 0, "🔧", 5),
    Mineral("Platina", TipoMineral.COMERCIAL, 100, "💰", 8),
    Mineral("Iridício", TipoMineral.TECNICO, 0, "🛡️", 7),
    Mineral("Elerium", TipoMineral.COMERCIAL, 200, "💰", 12),
    Mineral("Cristais de Energia", TipoMineral.TECNICO, 0, "⚡", 6),
    Mineral("Dark Matter", TipoMineral.COMERCIAL, 300, "💰", 20),
    Mineral("Antimatéria", TipoMineral.TECNICO, 0, "💥", 25)
]

# Definição de upgrades
UPGRADES_DISPONIVEIS = {
    "motor_fusao": {
        "creditos": 10000,
        "recursos": {"Hélio-3": 50},
        "descricao": "Permite viagens intergalácticas e aumenta tanque para 150"
    },
    "escudo_antimat": {
        "creditos": 25000,
        "recursos": {"Dark Matter": 20},
        "descricao": "Protege contra asteroides e eventos perigosos"
    },
    "broca_laser": {
        "creditos": 5000,
        "recursos": {"Cristais de Energia": 10},
        "descricao": "Aumenta velocidade de mineração em 50%"
    },
    "broca_reforcada": {
        "creditos": 3000,
        "recursos": {"Ouro": 5},
        "descricao": "Aumenta durabilidade máxima da broca para 150"
    },
    "broca_diamantada": {
        "creditos": 8000,
        "recursos": {"Cristais de Energia": 10},
        "descricao": "Broca praticamente indestrutível e 2x mais eficiente"
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
        [next(m for m in MINERAIS_DISPONIVEIS if m.nome == "Elerium"),
         next(m for m in MINERAIS_DISPONIVEIS if m.nome == "Cristais de Energia")],
        50,
        ["Alienígenas negociantes", "Distorção temporal"]
    ),
    Planeta(
        "Nebulosa do Dragão",
        [next(m for m in MINERAIS_DISPONIVEIS if m.nome == "Dark Matter"),
         next(m for m in MINERAIS_DISPONIVEIS if m.nome == "Antimatéria")],
        70,
        ["Nave Pirata", "Distorção temporal"]
    )
]

def mostrar_status(jogador):
    os.system('cls' if os.name == 'nt' else 'clear')
    
    print("\n=== 🚀 MINERADOR ESPACIAL AVANÇADO ===")
    print(f"👨‍🚀 Comandante: {jogador.nome}")
    print(f"🌟 Nível: {jogador.nivel} | 🔷 Experiência: {jogador.experiencia}/100")
    print(f"💰 Créditos: {jogador.creditos}")
    print(f"⛽ Combustível: {int(jogador.nave.combustivel)}/{jogador.nave.combustivel_max}")
    print(f"⚡ Estado da Nave: {100 - jogador.nave.dano}%")
    print(f"⛏️ Broca: {jogador.nave.broca_durabilidade}/{jogador.nave.broca_durabilidade_max}")
    if jogador.nave.broca_durabilidade <= 0:
        print("   ⚠️ BROCA MUITO DESGASTADA! (mineração 50% mais lenta)")
    
    print(f"\n🌌 Localização: {jogador.localizacao}")
    if jogador.planeta_atual:
        print(f"🌍 Planeta Atual: {jogador.planeta_atual.nome}")
        if jogador.planeta_atual.evento_ativo:
            print(f"   ⚠️ Evento Ativo: {jogador.planeta_atual.evento_ativo} ({jogador.planeta_atual.tempo_evento}s restantes)")
        
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
    print("\n=== ⚙️ UPGRADES DISPONÍVEIS ===")
    for upgrade, dados in UPGRADES_DISPONIVEIS.items():
        status = "✅" if jogador.nave.upgrades[upgrade] else "❌"
        print(f"\n{status} {upgrade.replace('_', ' ').title()}")
        print(f"   Preço: {dados['creditos']} créditos")
        print(f"   Recursos: {', '.join([f'{qtd} {nome}' for nome, qtd in dados['recursos'].items()])}")
        print(f"   Efeito: {dados['descricao']}")

def mostrar_planetas_disponiveis(jogador):
    print("\n=== 🌠 PLANETAS DISPONÍVEIS ===")
    
    if jogador.localizacao == "Via Láctea":
        planetas = PLANETAS_VIA_LACTEA
    else:
        planetas = PLANETAS_INTERGALACTICOS
    
    for i, planeta in enumerate(planetas):
        if planeta.nome in jogador.planetais_descobertos or jogador.localizacao == "Via Láctea":
            custo = int(planeta.dificuldade / jogador.nave.velocidade)
            print(f"{i+1}. {planeta.nome} - ⛽ Custo: {custo} - Dificuldade: {planeta.dificuldade}")
            
            if planeta.nome in jogador.planetais_visitados:
                minerais = [f"{m.icon} {m.nome}" for m in planeta.minerais]
                print(f"   Minérios: {' e '.join(minerais)}")
                print(f"   Eventos possíveis: {', '.join(planeta.eventos)}")
        else:
            print(f"{i+1}. Planeta desconhecido (explore para descobrir)")

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
        "5. Loja de upgrades",
        "6. Reparar nave",
        "7. Gerenciar combustível",
        "8. Reparar broca",
        "9. Sair do jogo"
    ])
    
    print("\n".join(opcoes))
    return input("\nEscolha uma ação: ")

def menu_combustivel(jogador):
    print("\n⛽ OPÇÕES DE COMBUSTÍVEL:")
    print(f"1. Comprar tanque pequeno (50 unidades) - 1.000 créditos")
    print(f"2. Recarga completa ({jogador.nave.combustivel_max} unidades) - 1.500 créditos")
    print("3. Voltar")
    
    opcao = input("Escolha uma opção: ")
    if opcao == "1":
        sucesso, mensagem = jogador.comprar_combustivel(50)
        print(mensagem)
    elif opcao == "2":
        sucesso, mensagem = jogador.comprar_combustivel(100)
        print(mensagem)
    elif opcao == "3":
        return
    else:
        print("⚠️ Opção inválida!")
    
    time.sleep(1.5)

def menu_reparo_broca(jogador):
    print(f"\n⚙️ ESTADO DA BROCA: {jogador.nave.broca_durabilidade}/{jogador.nave.broca_durabilidade_max}")
    if jogador.nave.broca_durabilidade <= 0:
        print("⚠️ SUA BROCA ESTÁ INUTILIZÁVEL! Repare para minerar normalmente.")
    
    print("\n🔧 OPÇÕES DE REPARO:")
    print("1. Reparo parcial (50%) - 500 créditos")
    print("2. Reparo total (100%) - 800 créditos")
    print("3. Reparo com recursos (2 Cobre para reparo total)")
    print("4. Voltar")
    
    opcao = input("Escolha uma opção: ")
    if opcao == "1":
        sucesso, mensagem = jogador.nave.reparar_broca(50)
        print(mensagem)
    elif opcao == "2":
        sucesso, mensagem = jogador.nave.reparar_broca(100)
        print(mensagem)
    elif opcao == "3":
        sucesso, mensagem = jogador.nave.reparar_broca(100, True, jogador)
        print(mensagem)
    elif opcao == "4":
        return
    else:
        print("⚠️ Opção inválida!")
    
    time.sleep(1.5)

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
    jogador_salvo = carregar_jogo()
    if jogador_salvo:
        jogador = jogador_salvo
        print("🚀 Jogo carregado com sucesso!")
    else:
        nome = input("👨‍🚀 Digite seu nome, Comandante: ")
        jogador = Jogador(nome)
        jogador.planetais_descobertos.update(p.nome for p in PLANETAS_VIA_LACTEA)
        print("\n🌌 Bem-vindo à Via Láctea, Comandante!")
        print("Explore planetas, colete minérios e melhore sua nave.")
        time.sleep(3)
    
    while True:
        mostrar_status(jogador)
        
        if jogador.planeta_atual:
            evento = jogador.planeta_atual.verificar_evento()
            if evento:
                print(f"\n⚠️ EVENTO: {evento}!")
                resultado = jogador.nave.aplicar_evento(evento)
                if resultado:
                    print(resultado)
                time.sleep(2)
            
            jogador.planeta_atual.atualizar_evento()
        
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
        
        if escolha == "1":
            if jogador.planeta_atual:
                print("\n💎 Minérios disponíveis:")
                for i, mineral in enumerate(jogador.planeta_atual.minerais):
                    print(f"{i+1}. {mineral.icon} {mineral.nome}")
                
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
            
            else:
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
                        
                        if jogador.localizacao != "Via Láctea" and not jogador.nave.upgrades["motor_fusao"]:
                            print("⚠️ Você precisa do Motor de Fusão para viajar entre galáxias!")
                            time.sleep(2)
                            continue
                        
                        custo = planeta.dificuldade / jogador.nave.velocidade
                        if jogador.nave.viajar(custo):
                            jogador.planeta_atual = planeta
                            jogador.planetais_visitados.add(planeta.nome)
                            print(f"🛸 Você chegou em {planeta.nome}!")
                            
                            if jogador.localizacao == "Via Láctea" and random.random() < 0.3:
                                novo_planeta = random.choice(PLANETAS_INTERGALACTICOS)
                                jogador.planetais_descobertos.add(novo_planeta.nome)
                                print(f"🔭 Você descobriu um novo planeta: {novo_planeta.nome}!")
                        else:
                            print("⚠️ Combustível insuficiente para viajar!")
                    else:
                        print("⚠️ Planeta inválido!")
                except ValueError:
                    print("⚠️ Por favor, digite um número válido!")
                time.sleep(2)
        
        elif escolha == "2" and jogador.planeta_atual:
            jogador.planeta_atual = None
            print("🚀 Você decolou para o espaço profundo")
            time.sleep(1)
        
        elif escolha == "3":
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
                        print(f"{i+1}. {mineral}: {qtd} unidades")
                    
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
        
        elif escolha == "4":
            valor = jogador.vender_minerais()
            if valor > 0:
                print(f"💰 Você vendeu minérios por {valor} créditos!")
            else:
                print("⚠️ Nenhum minério comercial para vender!")
            time.sleep(2)
        
        elif escolha == "5":
            while True:
                mostrar_upgrades(jogador)
                print("\n1. Voltar")
                print("2. Comprar upgrade")
                
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
                        print(f"{i+1}. {upgrade.replace('_', ' ').title()}")
                    
                    try:
                        opcao_up = int(input("Escolha o upgrade para comprar (0 para cancelar): ")) - 1
                        if opcao_up == -1:
                            continue
                            
                        if 0 <= opcao_up < len(upgrades_disponiveis):
                            upgrade = upgrades_disponiveis[opcao_up]
                            sucesso, mensagem = jogador.comprar_upgrade(upgrade)
                            print(mensagem)
                            
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

        elif escolha == "7":  # Gerenciar combustível
            menu_combustivel(jogador)
        
        elif escolha == "8":  # Reparar broca
            menu_reparo_broca(jogador)
        
        elif escolha == "9":  # Sair
            salvar_jogo(jogador)
            print("🚀 Progresso salvo. Até a próxima, Comandante!")
            break
        
        else:
            print("⚠️ Opção inválida!")
            time.sleep(1)

def menu_combustivel(jogador):
    print("\n⛽ OPÇÕES DE COMBUSTÍVEL:")
    print(f"1. Comprar tanque pequeno (50 unidades) - 1.000 créditos")
    print(f"2. Recarga completa ({jogador.nave.combustivel_max} unidades) - 1.500 créditos")
    print("3. Voltar")
    
    opcao = input("Escolha uma opção: ")
    if opcao == "1":
        sucesso, mensagem = jogador.comprar_combustivel(50)
        print(mensagem)
    elif opcao == "2":
        sucesso, mensagem = jogador.comprar_combustivel(100)
        print(mensagem)
    elif opcao == "3":
        return
    else:
        print("⚠️ Opção inválida!")
    
    time.sleep(1.5)

def menu_reparo_broca(jogador):
    print(f"\n⚙️ ESTADO DA BROCA: {jogador.nave.broca_durabilidade}/{jogador.nave.broca_durabilidade_max}")
    if jogador.nave.broca_durabilidade <= 0:
        print("⚠️ SUA BROCA ESTÁ INUTILIZÁVEL! Repare para minerar normalmente.")
    
    print("\n🔧 OPÇÕES DE REPARO:")
    print("1. Reparo parcial (50%) - 500 créditos")
    print("2. Reparo total (100%) - 800 créditos")
    print("3. Reparo com recursos (2 Cobre para reparo total)")
    print("4. Voltar")
    
    opcao = input("Escolha uma opção: ")
    if opcao == "1":
        sucesso, mensagem = jogador.nave.reparar_broca(50)
        print(mensagem)
    elif opcao == "2":
        sucesso, mensagem = jogador.nave.reparar_broca(100)
        print(mensagem)
    elif opcao == "3":
        sucesso, mensagem = jogador.nave.reparar_broca(100, True, jogador)
        print(mensagem)
    elif opcao == "4":
        return
    else:
        print("⚠️ Opção inválida!")
    
    time.sleep(1.5)

def carregar_jogo():
    try:
        with open('minerador_save.dat', 'rb') as f:
            return pickle.load(f)
    except:
        return None

def salvar_jogo(jogador):
    with open('minerador_save.dat', 'wb') as f:
        pickle.dump(jogador, f)

        if __name__ == "__main__":
    main()
