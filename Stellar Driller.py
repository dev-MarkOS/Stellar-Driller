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
                        print(f"{i + 1}. {upgrade.replace('_', ' ').title()}")

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