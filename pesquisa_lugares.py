"""Conteúdo pesquisado para os novos registros de Caicó.

Os textos abaixo são usados por app.py para cadastrar os locais uma única vez no MySQL.
As fontes consultadas estão documentadas em FONTES_PESQUISA_CAICO.md.
"""

SEED_CHAVE = "caico_lugares_pesquisa_2026_09_v1"

LUGARES_PESQUISADOS = [
    {
        "nome": "Antigo Casario Caicoense",
        "categoria": "Histórico",
        "localizacao": "Centro histórico de Caicó, Caicó-RN",
        "resumo": (
            "O Antigo Casario Caicoense reúne residências e outras construções do centro histórico "
            "que ajudam a contar o crescimento urbano, os modos de morar e as transformações "
            "arquitetônicas de Caicó ao longo do tempo."
        ),
        "historia": (
            "O centro antigo de Caicó concentra construções ligadas às diferentes etapas de formação e expansão da cidade. "
            "Esses imóveis registram mudanças na vida urbana e na arquitetura local, com exemplares associados a diferentes "
            "períodos e linguagens arquitetônicas.\n\n"
            "Pesquisas acadêmicas da UFRN tratam o casario como uma fonte importante para compreender o cotidiano da população "
            "caicoense. As casas não são vistas apenas como construções isoladas: seus ambientes, fachadas, materiais e alterações "
            "revelam formas de viver e de ocupar a cidade.\n\n"
            "Nas últimas décadas, parte desse patrimônio sofreu reformas descaracterizantes e demolições. Por isso, estudos de "
            "preservação têm defendido a valorização do conjunto remanescente e a adoção de boas práticas para conservar a memória "
            "arquitetônica do centro de Caicó."
        ),
        "curiosidades": (
            "Uma pesquisa publicada pela UFRN estudou exemplares do casario caicoense como artefatos capazes de revelar o modo cotidiano de viver na cidade.\n"
            "Uma dissertação defendida na UFRN em 2020 propôs boas práticas de intervenção e conservação para o casario antigo de Caicó.\n"
            "A perda e a descaracterização de imóveis antigos tornaram a preservação desse conjunto um tema recorrente nos estudos sobre patrimônio local."
        ),
        "imagem": None,
    },
    {
        "nome": "Capelinha do Serrote da Cruz",
        "categoria": "Histórico",
        "localizacao": "Serrote da Cruz, Ilha de Sant'Ana, Caicó-RN",
        "resumo": (
            "A Capelinha do Serrote da Cruz, dedicada a São Sebastião, é um espaço religioso e histórico situado em um dos pontos "
            "elevados da Ilha de Sant'Ana, com forte ligação com a devoção popular caicoense."
        ),
        "historia": (
            "A história religiosa do Serrote da Cruz começa no início do século XX. Em 1901, um cruzeiro foi colocado inicialmente "
            "em uma pequena ilha do rio Seridó e depois transferido para o serrote, contribuindo para o nome pelo qual o lugar passou a ser conhecido.\n\n"
            "Em cumprimento a uma promessa, foi construída uma pequena capela dedicada a São Sebastião. A capelinha foi inaugurada "
            "em 29 de setembro de 1940 e passou a reforçar a importância do serrote como espaço de devoção.\n\n"
            "A construção original desabou em 1966 devido à ação do tempo. Moradores e devotos preservaram a memória do lugar e, "
            "anos depois, organizaram a reconstrução. Os trabalhos começaram em 1º de abril de 1989 e foram concluídos em 20 de janeiro "
            "de 1990, dia de São Sebastião."
        ),
        "curiosidades": (
            "A cruz que deu nome ao Serrote da Cruz foi colocada na região no começo do século XX.\n"
            "São Sebastião é tradicionalmente associado à proteção contra a peste, a fome e a guerra.\n"
            "Do alto do serrote é possível observar partes da Ilha de Sant'Ana e do centro de Caicó."
        ),
        "imagem": None,
    },
    {
        "nome": "Restaurante Ponto Certo",
        "categoria": "Gastronômico",
        "localizacao": "Avenida Seridó, 720, Centro, Caicó-RN",
        "resumo": (
            "O Restaurante Ponto Certo é um estabelecimento tradicional de Caicó, voltado a refeições brasileiras, pizzas e opções "
            "para almoço e jantar no centro da cidade."
        ),
        "historia": (
            "Registros empresariais associam o nome fantasia Restaurante Ponto Certo a uma empresa aberta em 8 de janeiro de 1993, "
            "o que demonstra uma presença de décadas no setor de alimentação de Caicó.\n\n"
            "Ao longo desse período, o estabelecimento tornou-se conhecido no circuito gastronômico local. Guias de restaurantes o "
            "classificam principalmente entre as opções de culinária brasileira e pizza, atendendo tanto moradores quanto visitantes.\n\n"
            "Fontes cadastrais recentes indicam seu endereço na Avenida Seridó, no Centro, mantendo o restaurante inserido em uma das "
            "áreas mais movimentadas e tradicionais da cidade."
        ),
        "curiosidades": (
            "A atividade empresarial ligada ao Restaurante Ponto Certo aparece registrada desde janeiro de 1993.\n"
            "O estabelecimento é citado em guias locais e de viagem entre as opções de alimentação de Caicó.\n"
            "Seu perfil gastronômico combina refeições brasileiras e pizzas, com atendimento voltado a almoço e jantar."
        ),
        "imagem": None,
    },
    {
        "nome": "Itans e Piscicultura",
        "categoria": "Histórico",
        "localizacao": "Açude Itans e Estação de Piscicultura Estevão de Oliveira, cerca de 4 km a sudeste de Caicó-RN",
        "resumo": (
            "O Açude Itans e a Estação de Piscicultura Estevão de Oliveira formam um conjunto de grande importância histórica, hídrica "
            "e produtiva para Caicó e para o Seridó potiguar."
        ),
        "historia": (
            "Os primeiros estudos para o Açude Itans remontam ao início do século XX. A construção foi iniciada em 1932 no rio Barra Nova, "
            "em um contexto de forte seca no Nordeste, mobilizando grande quantidade de trabalhadores e estimulando atividades comerciais "
            "em Caicó. A obra foi concluída em 1935 e o reservatório foi inaugurado em fevereiro de 1936.\n\n"
            "Décadas depois, o DNOCS implantou junto ao açude a Estação de Piscicultura Estevão de Oliveira. A estação foi inaugurada em "
            "22 de abril de 1966 e iniciou suas operações de peixamento ainda naquele ano. Sua atuação se relaciona à reprodução de peixes "
            "de água doce e ao povoamento de açudes, lagoas e barragens.\n\n"
            "O conjunto representa duas estratégias importantes de convivência com o semiárido: o armazenamento de água e o aproveitamento "
            "dos reservatórios para produção pesqueira. O Itans também permanece como referência na memória coletiva de Caicó."
        ),
        "curiosidades": (
            "Um trecho sobre os trabalhadores da construção do Açude Itans foi usado em uma questão do ENEM 2022.\n"
            "A Estação de Piscicultura Estevão de Oliveira foi a terceira estação desse tipo construída pelo DNOCS no semiárido nordestino.\n"
            "Segundo o IFRN, a estação de Caicó é a única do Rio Grande do Norte dedicada à reprodução de peixes de água doce e participa do povoamento de reservatórios do estado."
        ),
        "imagem": None,
    },
    {
        "nome": "Mosteiro das Clarissas",
        "categoria": "Histórico",
        "localizacao": "Rua Irmã Coleta, 01, Caicó-RN",
        "resumo": (
            "O Mosteiro Nossa Senhora de Guadalupe, conhecido como Mosteiro das Clarissas, é um importante espaço de vida contemplativa "
            "e de história religiosa em Caicó, ligado à Ordem de Santa Clara."
        ),
        "historia": (
            "A fundação do Mosteiro Nossa Senhora de Guadalupe ocorreu em 17 de junho de 1984, após pedidos do então bispo da Diocese de Caicó, "
            "Dom Heitor de Araújo Sales, para a instalação de uma comunidade clariana na região.\n\n"
            "O grupo fundador veio do Mosteiro Nossa Senhora dos Anjos, no Rio de Janeiro. Oito religiosas participaram da nova fundação, "
            "tendo Madre Maria Coleta entre as responsáveis pela implantação da comunidade. Nos primeiros anos, as irmãs ficaram instaladas "
            "provisoriamente no Castelo de Engady.\n\n"
            "Em 1987, a comunidade seguiu em procissão para o edifício definitivo do mosteiro. A presença das Clarissas consolidou em Caicó "
            "um espaço dedicado à oração, à vida contemplativa e à tradição franciscana."
        ),
        "curiosidades": (
            "A fundação de Caicó foi o primeiro mosteiro da Ordem de Santa Clara implantado no Rio Grande do Norte.\n"
            "As religiosas fundadoras chegaram a Caicó em junho de 1984 e passaram os primeiros anos no Castelo de Engady.\n"
            "O nome oficial é Mosteiro Nossa Senhora de Guadalupe — Mãe das Américas."
        ),
        "imagem": None,
    },
    {
        "nome": "Panificadora Seridó",
        "categoria": "Gastronômico",
        "localizacao": "Rua Major Lula, 1010, bairro Paraíba, Caicó-RN",
        "resumo": (
            "A Panificadora e Restaurante Seridó é uma referência tradicional de alimentação em Caicó, reunindo serviços de padaria, "
            "café da manhã, almoço e opções para o período noturno."
        ),
        "historia": (
            "Uma pesquisa acadêmica da UFRN sobre turismo e serviços em Caicó registra a Panificadora e Restaurante Seridó como inaugurada "
            "em 1977, indicando sua longa presença na atividade gastronômica do município.\n\n"
            "O estabelecimento ampliou sua proposta para além da panificação. Em sua apresentação institucional, destaca serviços de café da manhã, "
            "almoço com pratos do dia e comidas típicas da região, além de opções para jantar, petiscos, pizzas e sobremesas.\n\n"
            "A combinação de panificação e restaurante ajuda a explicar sua presença no cotidiano da cidade, atendendo diferentes momentos do dia "
            "e valorizando também pratos associados à alimentação regional."
        ),
        "curiosidades": (
            "Pesquisa da UFRN registra 1977 como ano de inauguração da Panificadora e Restaurante Seridó.\n"
            "O estabelecimento oferece desde café da manhã até almoço e jantar.\n"
            "Fontes atuais de eventos e turismo em Caicó indicam a unidade na Rua Major Lula, 1010, bairro Paraíba."
        ),
        "imagem": None,
    },
    {
        "nome": "Praça da Liberdade",
        "categoria": "Histórico",
        "localizacao": "Praça Senador Dinarte Mariz (Praça da Liberdade / Praça do Coreto), Centro, Caicó-RN",
        "resumo": (
            "A Praça da Liberdade, oficialmente Praça Senador Dinarte Mariz e também conhecida como Praça do Coreto, é um dos espaços públicos "
            "mais carregados de memória política e social do centro de Caicó."
        ),
        "historia": (
            "A história da praça está ligada ao antigo Mercado Público de Caicó, construído por volta de 1870. Por esse motivo, o espaço foi "
            "conhecido inicialmente como Praça do Mercado e funcionou como importante ponto de comércio e convivência.\n\n"
            "O local também ficou relacionado a episódios marcantes da história da cidade, entre eles a Revolta do Quebra-Quilos e a atuação do "
            "movimento abolicionista. Pesquisas sobre o espaço registram que ali eram concedidas cartas de alforria, associando o lugar à ideia de liberdade.\n\n"
            "Com a transferência do mercado, em 1918, a área passou por mudanças e recebeu um coreto de madeira. O coreto foi substituído em 1931 "
            "e novamente em 1943 pelo modelo que se tornou uma referência visual da praça. O nome oficial foi posteriormente alterado para Praça Senador "
            "Dinarte Mariz, mas a população continua usando amplamente o nome Praça da Liberdade."
        ),
        "curiosidades": (
            "A praça já foi conhecida como Praça do Mercado, Praça da Liberdade, Praça do Coreto e oficialmente Praça Senador Dinarte Mariz.\n"
            "O primeiro coreto foi construído em madeira em 1918; o coreto atual deriva de uma substituição realizada em 1943.\n"
            "Mesmo após a mudança do nome oficial, 'Praça da Liberdade' permanece fortemente presente na memória e no uso cotidiano dos caicoenses."
        ),
        "imagem": None,
    },
    {
        "nome": "Carvoeiro",
        "categoria": "Gastronômico",
        "localizacao": "Praça Valfredo Gurgel, 23, Centro, Caicó-RN",
        "resumo": (
            "O Carvoeiro integra a cena gastronômica contemporânea de Caicó como restaurante e bar, com destaque para churrasco, cozinha brasileira "
            "e um ambiente voltado a refeições e encontros."
        ),
        "historia": (
            "O Carvoeiro aparece em fontes recentes de gastronomia e turismo como um dos estabelecimentos localizados na região central de Caicó. "
            "Diferentemente de patrimônios históricos da cidade, há pouca documentação pública disponível sobre a data de fundação ou os primeiros anos "
            "do negócio.\n\n"
            "As informações atuais o apresentam como restaurante, bar e espaço de churrasco, com atendimento para almoço, jantar e bebidas. A localização "
            "na Praça Valfredo Gurgel coloca o estabelecimento dentro do circuito de convivência e alimentação do centro.\n\n"
            "Por representar uma atividade gastronômica atual, sua inclusão na Memória Potiguar também registra como os espaços de alimentação contemporâneos "
            "participam da vida social da cidade."
        ),
        "curiosidades": (
            "Guias gastronômicos classificam o Carvoeiro entre cozinha brasileira, churrasco, bar e pub.\n"
            "O estabelecimento é indicado em materiais recentes de eventos acadêmicos entre os locais para comer e beber em Caicó.\n"
            "Fica na Praça Valfredo Gurgel, no Centro da cidade."
        ),
        "imagem": None,
    },
    {
        "nome": "Praça José Augusto",
        "categoria": "Cultural",
        "localizacao": "Praça Dr. José Augusto (Praça da Alimentação), Centro, Caicó-RN",
        "resumo": (
            "A Praça Dr. José Augusto, conhecida como Praça da Alimentação, é um importante espaço de convivência, lazer e gastronomia no centro de Caicó."
        ),
        "historia": (
            "Antes de se consolidar como Praça da Alimentação, a Praça Dr. José Augusto já era um tradicional espaço de encontro no centro de Caicó. "
            "A partir da década de 1980, trailers de lanches e comidas passaram a ocupar gradualmente a área, fortalecendo sua ligação com a gastronomia.\n\n"
            "Com o crescimento do número de trailers, o lugar ficou popularmente conhecido também como Praça dos Trailers. Entre 2008 e 2010, o espaço "
            "passou por uma ampla reconfiguração que substituiu a antiga organização por quiosques padronizados e consolidou a função de praça de alimentação.\n\n"
            "A nova Praça da Alimentação foi inaugurada em março de 2010. Desde então, o espaço permanece ligado a restaurantes, lanchonetes, encontros entre "
            "amigos e familiares e atividades realizadas no centro da cidade."
        ),
        "curiosidades": (
            "A praça também ficou conhecida como Praça dos Trailers devido à presença de trailers de alimentação antes da grande reforma.\n"
            "A transformação mais recente em Praça da Alimentação ocorreu entre 2008 e 2010.\n"
            "Além da gastronomia, o espaço é usado para encontros, lazer e atividades públicas, reforçando seu papel como ponto de sociabilidade em Caicó."
        ),
        "imagem": None,
    },
]
