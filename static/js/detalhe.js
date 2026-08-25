(function () {
    const main = document.querySelector('.detalhe-container');
    if (!main) return;

    const titleEl = main.querySelector('.detalhe-titulo');
    const subtitleEl = main.querySelector('.detalhe-subtitulo');
    const sections = Array.from(main.querySelectorAll(':scope > section'));
    if (!titleEl || !sections.length) return;

    const clean = (text) => (text || '').replace(/\s+/g, ' ').trim();
    const normalize = (text) => clean(text).normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase();
    const title = clean(titleEl.textContent);
    const subtitle = clean(subtitleEl ? subtitleEl.textContent : 'Conheça a história e a importância deste lugar para a memória potiguar.');

    const path = location.pathname.toLowerCase();
    let category = 'CULTURAL';
    if (path.includes('gastronom')) category = 'GASTRONÔMICO';
    else if (path.includes('histor')) category = 'HISTÓRICO';
    else if (path.includes('evento') || path.includes('festa')) category = 'EVENTO';

    const gallerySection = sections.find(s => normalize(s.querySelector('h2')?.textContent).includes('galeria'));
    const firstImage = gallerySection?.querySelector('img') || main.querySelector('img');
    const heroImage = firstImage ? firstImage.getAttribute('src') : '';

    const locationSection = sections.find(s => normalize(s.querySelector('h2')?.textContent).includes('localiza'));
    let locationText = 'Rio Grande do Norte';
    if (locationSection) {
        const p = locationSection.querySelector('p');
        locationText = clean(p?.textContent.replace(/^Endereço:\s*/i, '')) || locationText;
    }

    // HERO
    const hero = document.createElement('section');
    hero.className = 'lugar-hero';
    if (heroImage) hero.style.backgroundImage = `linear-gradient(90deg, rgba(25,18,13,.75), rgba(25,18,13,.28)), url("${heroImage}")`;
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

    // TABS no padrão da referência
    const tabsData = [
        ['▣', 'Sobre', 'sobre'],
        ['▤', 'História', 'historia'],
        ['✦', 'Localização', 'localizacao'],
        ['▦', 'Dados e Informações', 'dados'],
        ['▧', 'Galeria', 'galeria'],
        ['▣', 'Eventos Relacionados', 'eventos']
    ];
    const tabs = document.createElement('nav');
    tabs.className = 'lugar-tabs';
    tabs.innerHTML = `<div class="lugar-tabs-inner">${tabsData.map((t,i)=>`<a href="#${t[2]}" data-target="${t[2]}" class="${i===0?'active':''}"><span>${t[0]}</span>${t[1]}</a>`).join('')}</div>`;
    main.parentNode.insertBefore(tabs, main);

    // Identifica e ordena as seções existentes
    function kind(section) {
        const txt = normalize(section.querySelector('h2')?.textContent);
        if (txt.includes('localiza')) return 'localizacao';
        if (txt.includes('galeria')) return 'galeria';
        if (txt.includes('evento')) return 'eventos';
        if (txt.includes('dado') || txt.includes('informac')) return 'dados';
        if (txt.includes('hist') || txt.includes('cultura') || txt.includes('sobre') || txt.includes('conhe')) return 'sobre';
        return 'sobre';
    }
    const order = {sobre:0, localizacao:1, dados:2, galeria:3, eventos:4};
    sections.sort((a,b)=>order[kind(a)]-order[kind(b)]);

    const layout = document.createElement('div');
    layout.className = 'lugar-layout';
    const aside = document.createElement('aside');
    aside.className = 'lugar-sidebar';
    aside.innerHTML = `<strong>NESTA PÁGINA</strong>${tabsData.map((t,i)=>`<a href="#${t[2]}" class="${i===0?'active':''}"><span>•</span>${t[1]}</a>`).join('')}`;
    const content = document.createElement('div');
    content.className = 'lugar-conteudo';

    let hasSobre = false;
    sections.forEach(section => {
        const k = kind(section);
        if (k === 'sobre' && !hasSobre) {
            section.id = 'sobre';
            hasSobre = true;
            const h2 = section.querySelector('h2');
            if (h2) h2.innerHTML = '<span class="secao-icone">▤</span> Sobre';
        } else {
            section.id = k;
        }
        content.appendChild(section);
    });

    // Âncoras auxiliares para abas que não têm uma seção própria.
    if (hasSobre && !document.getElementById('historia')) {
        const historyAnchor = document.createElement('span');
        historyAnchor.id = 'historia';
        historyAnchor.className = 'anchor-proxy';
        content.querySelector('#sobre').prepend(historyAnchor);
    }
    ['dados','eventos'].forEach(id => {
        if (!document.getElementById(id)) {
            const proxy = document.createElement('span');
            proxy.id = id;
            proxy.className = 'anchor-proxy';
            (content.querySelector('#sobre') || content).appendChild(proxy);
        }
    });

    layout.appendChild(aside);
    layout.appendChild(content);

    titleEl.remove();
    if (subtitleEl) subtitleEl.remove();
    main.prepend(layout);

    const back = Array.from(main.querySelectorAll('a.btn')).find(a => normalize(a.textContent).includes('voltar'));
    if (back) {
        back.classList.add('btn-voltar-detalhe');
        main.appendChild(back);
    }

    // Navegação ativa
    const navLinks = document.querySelectorAll('.lugar-tabs a, .lugar-sidebar a');
    navLinks.forEach(link => link.addEventListener('click', () => {
        const target = link.getAttribute('href');
        navLinks.forEach(l => l.classList.toggle('active', l.getAttribute('href') === target));
    }));
})();
