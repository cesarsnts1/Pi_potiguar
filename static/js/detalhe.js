(function () {
    const main = document.querySelector('.detalhe-container');
    if (!main) return;

    const titleEl = main.querySelector('.detalhe-titulo');
    const subtitleEl = main.querySelector('.detalhe-subtitulo');
    if (!titleEl) return;

    const clean = (text) => (text || '').replace(/\s+/g, ' ').trim();
    const normalize = (text) => clean(text)
        .normalize('NFD')
        .replace(/[\u0300-\u036f]/g, '')
        .toLowerCase();

    const title = clean(titleEl.textContent);
    const subtitle = clean(
        subtitleEl ? subtitleEl.textContent : 'Conheça este lugar e sua importância para a memória potiguar.'
    );

    // A categoria agora vem marcada no próprio HTML de cada página.
    // Há um fallback apenas para páginas antigas que ainda não tenham data-categoria.
    let category = clean(main.dataset.categoria);
    if (!category) {
        const path = location.pathname.toLowerCase();
        if (path.includes('gastronom')) category = 'GASTRONÔMICO';
        else if (path.includes('evento') || path.includes('festa')) category = 'EVENTO';
        else category = 'CULTURAL';
    }

    const allSections = Array.from(main.querySelectorAll('section.info-secao, section.galeria-secao')); // aceita páginas antigas mesmo se alguma seção estiver aninhada
    if (!allSections.length) return;

    const gallerySection = allSections.find(section =>
        section.dataset.secao === 'galeria' ||
        normalize(section.querySelector('h2')?.textContent).includes('galeria')
    );
    const firstImage = gallerySection?.querySelector('img') || main.querySelector('img');
    const heroImage = firstImage ? firstImage.getAttribute('src') : '';

    const locationSection = allSections.find(section =>
        section.dataset.secao === 'localizacao' ||
        normalize(section.querySelector('h2')?.textContent).includes('localiza')
    );
    let locationText = 'Rio Grande do Norte';
    if (locationSection) {
        const p = locationSection.querySelector('p');
        locationText = clean(p?.textContent.replace(/^Endereço:\s*/i, '')) || locationText;
    }

    // HERO
    const hero = document.createElement('section');
    hero.className = 'lugar-hero';
    if (heroImage) {
        hero.style.backgroundImage = `linear-gradient(90deg, rgba(25,18,13,.78), rgba(25,18,13,.30)), url("${heroImage}")`;
    }
    hero.innerHTML = `
        <div class="lugar-hero-inner">
            <div class="lugar-hero-copy">
                <span class="lugar-categoria">${category}</span>
                <h1>${title}</h1>
                <p>${subtitle}</p>
                <div class="lugar-localizacao">✦ ${locationText}</div>
            </div>
            ${heroImage ? `<div class="lugar-thumb"><img src="${heroImage}" alt="${title}"></div>` : ''}
        </div>`;
    main.parentNode.insertBefore(hero, main);

    function sectionKind(section) {
        if (section.dataset.secao) return section.dataset.secao;
        const text = normalize(section.querySelector('h2')?.textContent);
        if (text.includes('resumo') || text.includes('sobre')) return 'resumo';
        if (text.includes('hist')) return 'historia';
        if (text.includes('curios')) return 'curiosidades';
        if (text.includes('localiza')) return 'localizacao';
        if (text.includes('galeria')) return 'galeria';
        return 'outros';
    }

    const labels = {
        resumo: ['▤', 'Resumo'],
        historia: ['◷', 'História'],
        curiosidades: ['✦', 'Curiosidades'],
        localizacao: ['⌖', 'Localização'],
        galeria: ['▧', 'Galeria']
    };
    const order = ['resumo', 'historia', 'curiosidades', 'localizacao', 'galeria'];

    const sectionMap = new Map();
    allSections.forEach(section => {
        const kind = sectionKind(section);
        if (kind !== 'outros' && !sectionMap.has(kind)) {
            sectionMap.set(kind, section);
            section.id = kind;
            section.dataset.secao = kind;
        }
    });

    // Só mostra abas para seções que realmente existem na página.
    const availableTabs = order.filter(key => sectionMap.has(key));

    const tabs = document.createElement('nav');
    tabs.className = 'lugar-tabs';
    tabs.setAttribute('aria-label', 'Navegação da página');
    tabs.innerHTML = `<div class="lugar-tabs-inner">${availableTabs.map((key, index) => {
        const [icon, label] = labels[key];
        return `<a href="#${key}" class="${index === 0 ? 'active' : ''}"><span>${icon}</span>${label}</a>`;
    }).join('')}</div>`;
    main.parentNode.insertBefore(tabs, main);

    const layout = document.createElement('div');
    layout.className = 'lugar-layout';

    const aside = document.createElement('aside');
    aside.className = 'lugar-sidebar';
    aside.innerHTML = `
        <strong>NESTA PÁGINA</strong>
        ${availableTabs.map((key, index) => {
            const [, label] = labels[key];
            return `<a href="#${key}" class="${index === 0 ? 'active' : ''}"><span>•</span>${label}</a>`;
        }).join('')}`;

    const content = document.createElement('div');
    content.className = 'lugar-conteudo';

    order.forEach(key => {
        const section = sectionMap.get(key);
        if (!section) return;
        const h2 = section.querySelector('h2');
        if (h2 && labels[key]) {
            h2.innerHTML = `<span class="secao-icone">${labels[key][0]}</span> ${labels[key][1]}`;
        }
        content.appendChild(section);
    });

    // Mantém qualquer seção extra, caso alguma página tenha conteúdo específico no futuro.
    allSections.forEach(section => {
        if (!content.contains(section)) content.appendChild(section);
    });

    layout.appendChild(aside);
    layout.appendChild(content);

    titleEl.remove();
    if (subtitleEl) subtitleEl.remove();
    main.prepend(layout);

    const back = Array.from(main.querySelectorAll('a.btn')).find(a =>
        normalize(a.textContent).includes('voltar')
    );
    if (back) {
        back.classList.add('btn-voltar-detalhe');
        main.appendChild(back);
    }

    const navLinks = Array.from(document.querySelectorAll('.lugar-tabs a, .lugar-sidebar a'));
    const activate = (hash) => {
        navLinks.forEach(link => link.classList.toggle('active', link.getAttribute('href') === hash));
    };

    navLinks.forEach(link => {
        link.addEventListener('click', () => activate(link.getAttribute('href')));
    });

    // Atualiza o item ativo enquanto o visitante rola a página.
    if ('IntersectionObserver' in window) {
        const observer = new IntersectionObserver(entries => {
            const visible = entries
                .filter(entry => entry.isIntersecting)
                .sort((a, b) => b.intersectionRatio - a.intersectionRatio)[0];
            if (visible?.target?.id) activate(`#${visible.target.id}`);
        }, { rootMargin: '-20% 0px -55% 0px', threshold: [0.1, 0.35, 0.6] });

        availableTabs.forEach(key => observer.observe(sectionMap.get(key)));
    }
})();
