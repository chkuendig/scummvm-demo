class GamesLibrary {
	constructor() {
		this.gamesData = [];
		this.gamesMetadata = {};
		this.companiesMetadata = {};
		this.enginesMetadata = {};
		this.iconIndex = {};
		this.groupedGames = {};
		this.gameRecords = [];
		this.companyOptions = new Map();
		this.engineOptions = new Map();
		this.filters = {
			search: '',
			company: 'all',
			engine: 'all'
		};
		this.currentSort = 'alpha';
		this.sortDirection = 'asc';

		this.dom = {
			loading: document.getElementById('loading'),
			error: document.getElementById('error'),
			content: document.getElementById('content'),
			gamesList: document.getElementById('gamesList'),
			searchBox: document.getElementById('searchBox'),
			companyFilter: document.getElementById('companyFilter'),
			engineFilter: document.getElementById('engineFilter'),
			sortButtons: document.querySelectorAll('.sort-button')
		};

		this.init();
	}

	async init() {
		try {
			await this.loadData();
			this.processData();
			this.populateFilterOptions();
			this.setupControls();
			this.updateDisplay();
			this.showContent();
		} catch (error) {
			console.error('Error initializing games library:', error);
			this.showError();
		}
	}

	async loadData() {
		const gamesResponse = await fetch('./games.json');
		this.gamesData = await gamesResponse.json();

		const indexResponse = await fetch('data/gui-icons/icons/index.json');
		this.iconIndex = await indexResponse.json();

		const gamesXmlResponse = await fetch('data/gui-icons/games.xml');
		const gamesXmlText = await gamesXmlResponse.text();
		this.parseGamesXml(gamesXmlText);

		const companiesXmlResponse = await fetch('data/gui-icons/companies.xml');
		const companiesXmlText = await companiesXmlResponse.text();
		this.parseCompaniesXml(companiesXmlText);

		const enginesXmlResponse = await fetch('data/gui-icons/engines.xml');
		const enginesXmlText = await enginesXmlResponse.text();
		this.parseEnginesXml(enginesXmlText);
	}

	parseGamesXml(xmlText) {
		if (!xmlText) return;
		const parser = new DOMParser();
		const doc = parser.parseFromString(xmlText, 'text/xml');
		const gameElements = doc.getElementsByTagName('game');

		for (let i = 0; i < gameElements.length; i++) {
			const game = gameElements[i];
			const id = game.getAttribute('id');
			if (!id) continue;

			const engineId = game.getAttribute('engine_id') || null;
			const metadata = {
				name: game.getAttribute('name') || '',
				companyId: game.getAttribute('company_id') || null,
				engineId,
				year: this.parseYear(game.getAttribute('year'))
			};

			this.storeGameMetadata(id, engineId, metadata);
		}
	}

	storeGameMetadata(gameId, engineId, metadata) {
		if (engineId) {
			const compositeKey = `${engineId}:${gameId}`;
			this.gamesMetadata[compositeKey] = metadata;
		}

		if (!Object.prototype.hasOwnProperty.call(this.gamesMetadata, gameId)) {
			this.gamesMetadata[gameId] = metadata;
		}
	}

	parseYear(value) {
		const parsed = parseInt(value, 10);
		return Number.isFinite(parsed) ? parsed : null;
	}

	parseCompaniesXml(xmlText) {
		if (!xmlText) return;
		const parser = new DOMParser();
		const doc = parser.parseFromString(xmlText, 'text/xml');
		const companyElements = doc.getElementsByTagName('company');

		for (let i = 0; i < companyElements.length; i++) {
			const company = companyElements[i];
			const id = company.getAttribute('id');
			if (!id) continue;
			this.companiesMetadata[id] = {
				name: company.getAttribute('name') || '',
				altName: company.getAttribute('alt_name') || ''
			};
		}
	}

	parseEnginesXml(xmlText) {
		if (!xmlText) return;
		const parser = new DOMParser();
		const doc = parser.parseFromString(xmlText, 'text/xml');
		const engineElements = doc.getElementsByTagName('engine');

		for (let i = 0; i < engineElements.length; i++) {
			const engine = engineElements[i];
			const id = engine.getAttribute('id');
			if (!id) continue;
			this.enginesMetadata[id] = {
				name: engine.getAttribute('name') || '',
				altName: engine.getAttribute('alt_name') || ''
			};
		}
	}

	processData() {
		this.groupGames();
		this.gameRecords = [];
		this.companyOptions.clear();
		this.engineOptions.clear();

		Object.entries(this.groupedGames).forEach(([gameId, variants]) => {
			if (!variants || variants.length === 0) {
				return;
			}

			const primaryVariant = this.selectPrimaryVariant(variants);
			if (!primaryVariant) {
				return;
			}

			const gameInfo = this.enrichGameInfo(gameId, primaryVariant);
			const iconPath = this.getIconPath(gameId);
			const launchUrl = this.buildLaunchUrl(gameId, primaryVariant);
			const languages = Array.isArray(primaryVariant.languages) ? primaryVariant.languages : [];
			const description = primaryVariant.description || '';
			const platform = primaryVariant.platform || 'Unknown';

			const record = {
				gameId,
				gameIdLower: gameId.toLowerCase(),
				name: gameInfo.name,
				nameLower: gameInfo.name.toLowerCase(),
				companyId: gameInfo.companyId,
				companyName: gameInfo.companyName,
				companyLower: (gameInfo.companyName || '').toLowerCase(),
				engineId: gameInfo.engineId,
				engineName: gameInfo.engineName,
				year: gameInfo.year,
				variant: primaryVariant,
				launchUrl,
				iconPath,
				languages,
				platform,
				description,
				descriptionLower: description.toLowerCase()
			};

			this.gameRecords.push(record);

			if (record.companyId && record.companyName) {
				this.companyOptions.set(record.companyId, record.companyName);
			}
			if (record.engineId && record.engineName) {
				this.engineOptions.set(record.engineId, record.engineName);
			}
		});
	}

	groupGames() {
		this.groupedGames = {};
		this.gamesData.forEach(entry => {
			if (!entry.id) return;
			if (!this.groupedGames[entry.id]) {
				this.groupedGames[entry.id] = [];
			}
			this.groupedGames[entry.id].push(entry);
		});
	}

	selectPrimaryVariant(variants) {
		if (!variants || variants.length === 0) {
			return null;
		}
		return variants.find(variant => variant.cover) ||
			variants.find(variant => variant.description) ||
			variants[0];
	}

	enrichGameInfo(gameId, variant) {
		const metadata = this.getGameMetadata(gameId) || {};
		const simpleId = this.extractSimpleId(gameId);

		const nameCandidate = metadata.name || variant.name;
		const name = nameCandidate || this.formatGameId(simpleId);

		const companyId = metadata.companyId || null;
		let companyName = companyId ? this.getCompanyName(companyId) : null;
		if (!companyName && variant.company) {
			companyName = variant.company;
		}

		const engineId = metadata.engineId || null;
		const engineName = engineId ? this.getEngineName(engineId) : null;

		return {
			name,
			companyId,
			companyName,
			engineId,
			engineName,
			year: metadata.year
		};
	}

	getGameMetadata(gameId) {
		if (!gameId) {
			return null;
		}

		if (Object.prototype.hasOwnProperty.call(this.gamesMetadata, gameId)) {
			return this.gamesMetadata[gameId];
		}

		const simpleId = this.extractSimpleId(gameId);
		if (simpleId !== gameId && Object.prototype.hasOwnProperty.call(this.gamesMetadata, simpleId)) {
			return this.gamesMetadata[simpleId];
		}

		return null;
	}

	extractSimpleId(gameId) {
		const segments = gameId.split(':');
		return segments.length > 1 ? segments[1] : segments[0];
	}

	formatGameId(rawId) {
		if (!rawId) return '';
		return rawId
			.replace(/[_-]/g, ' ')
			.replace(/\s+/g, ' ')
			.trim()
			.replace(/\b\w/g, char => char.toUpperCase());
	}

	getCompanyName(companyId) {
		const entry = this.companiesMetadata[companyId];
		if (!entry) return null;
		return entry.name || entry.altName || null;
	}

	getEngineName(engineId) {
		const entry = this.enginesMetadata[engineId];
		if (!entry) return null;
		return entry.name || entry.altName || null;
	}

	buildLaunchUrl(gameId, variant) {
		if (!variant) return '#';
		const params = [`--path=/data/games/${variant.relative_path}`];

		if (variant.languages && variant.languages.length > 0) {
			const primaryLang = variant.languages[0];
			if (primaryLang && primaryLang !== 'Unknown') {
				const shortLang = primaryLang.includes('_') ? primaryLang.split('_').pop() : primaryLang;
				params.push(`--language=${shortLang.toLowerCase()}`);
			}
		}

		return `scummvm.html#${params.join(' ')} ${gameId}`;
	}

	populateFilterOptions() {
		this.populateSelect(this.dom.companyFilter, this.companyOptions);
		this.populateSelect(this.dom.engineFilter, this.engineOptions);
	}

	populateSelect(selectElement, optionsMap) {
		if (!selectElement) return;
		while (selectElement.options.length > 1) {
			selectElement.remove(1);
		}
		const options = Array.from(optionsMap.entries()).sort((a, b) => a[1].localeCompare(b[1]));
		options.forEach(([value, label]) => {
			const option = document.createElement('option');
			option.value = value;
			option.textContent = label;
			selectElement.appendChild(option);
		});
	}

	getIconPath(gameId) {
		const engineGameId = gameId.replace(':', '-');
		const iconFileName = `${engineGameId}.png`;

		if (this.iconIndex && Object.prototype.hasOwnProperty.call(this.iconIndex, iconFileName)) {
			return `data/gui-icons/icons/${iconFileName}`;
		}

		return null;
	}

	setupControls() {
		if (this.dom.searchBox) {
			this.dom.searchBox.addEventListener('input', event => {
				this.filters.search = event.target.value.trim().toLowerCase();
				this.updateDisplay();
			});
		}

		if (this.dom.companyFilter) {
			this.dom.companyFilter.addEventListener('change', event => {
				const value = event.target.value;
				this.filters.company = value;
				if (value !== 'all' && this.dom.engineFilter) {
					this.filters.engine = 'all';
					this.dom.engineFilter.value = 'all';
				}
				this.updateDisplay();
			});
		}

		if (this.dom.engineFilter) {
			this.dom.engineFilter.addEventListener('change', event => {
				const value = event.target.value;
				this.filters.engine = value;
				if (value !== 'all' && this.dom.companyFilter) {
					this.filters.company = 'all';
					this.dom.companyFilter.value = 'all';
				}
				this.updateDisplay();
			});
		}

		if (this.dom.sortButtons && this.dom.sortButtons.length > 0) {
			this.dom.sortButtons.forEach(button => {
				if (!button.dataset.label) {
					button.dataset.label = button.textContent.trim();
				}
				if (!button.dataset.defaultDirection) {
					button.dataset.defaultDirection = 'asc';
				}

				button.addEventListener('click', () => {
					const sortKey = button.getAttribute('data-sort');
					if (this.currentSort === sortKey) {
						this.sortDirection = this.sortDirection === 'asc' ? 'desc' : 'asc';
					} else {
						this.currentSort = sortKey;
						this.sortDirection = this.getDefaultSortDirection(sortKey);
					}
					this.updateSortButtonState();
					this.updateDisplay();
				});
			});
			this.updateSortButtonState();
		}
	}

	updateSortButtonState() {
		if (!this.dom.sortButtons) return;
		this.dom.sortButtons.forEach(button => {
			const isActive = button.getAttribute('data-sort') === this.currentSort;
			const baseLabel = button.dataset.label || button.textContent.trim();
			let label = baseLabel;

			if (isActive) {
				button.classList.add('active');
				button.setAttribute('aria-pressed', 'true');
				const arrow = this.sortDirection === 'asc' ? '▲' : '▼';
				label = `${baseLabel} ${arrow}`;
			} else {
				button.classList.remove('active');
				button.setAttribute('aria-pressed', 'false');
			}

			button.textContent = label;
		});
	}

	getDefaultSortDirection(sortKey) {
		if (!this.dom.sortButtons) {
			return 'asc';
		}

		const buttons = Array.from(this.dom.sortButtons);
		const match = buttons.find(btn => btn.getAttribute('data-sort') === sortKey);
		if (match && match.dataset.defaultDirection) {
			return match.dataset.defaultDirection === 'desc' ? 'desc' : 'asc';
		}

		return 'asc';
	}

	updateDisplay() {
		const filteredRecords = this.getFilteredRecords();
		const sortedRecords = this.sortRecords(filteredRecords);
		this.renderGames(sortedRecords);
	}

	getFilteredRecords() {
		const searchTerm = this.filters.search;
		const companyFilter = this.filters.company;
		const engineFilter = this.filters.engine;

		return this.gameRecords.filter(record => {
			const matchesSearch = !searchTerm ||
				record.nameLower.includes(searchTerm) ||
				record.companyLower.includes(searchTerm) ||
				record.gameIdLower.includes(searchTerm) ||
				record.descriptionLower.includes(searchTerm);

			if (!matchesSearch) {
				return false;
			}

			const matchesCompany = companyFilter === 'all' || record.companyId === companyFilter;
			if (!matchesCompany) {
				return false;
			}

			const matchesEngine = engineFilter === 'all' || record.engineId === engineFilter;
			if (!matchesEngine) {
				return false;
			}

			return true;
		});
	}

	sortRecords(records) {
		const sorted = [...records];
		const direction = this.sortDirection === 'asc' ? 1 : -1;

		if (this.currentSort === 'year') {
			const fallback = this.sortDirection === 'asc' ? Number.MAX_SAFE_INTEGER : Number.MIN_SAFE_INTEGER;
			sorted.sort((a, b) => {
				const yearA = Number.isFinite(a.year) ? a.year : fallback;
				const yearB = Number.isFinite(b.year) ? b.year : fallback;
				const diff = yearA - yearB;
				if (diff !== 0) {
					return diff * direction;
				}
				return a.nameLower.localeCompare(b.nameLower) * direction;
			});
		} else {
			sorted.sort((a, b) => a.nameLower.localeCompare(b.nameLower) * direction);
		}
		return sorted;
	}

	renderGames(records) {
		if (!this.dom.gamesList) return;

		this.dom.gamesList.innerHTML = '';

		if (records.length === 0) {
			const empty = document.createElement('div');
			empty.className = 'empty-state';
			empty.textContent = 'No games match the current filters.';
			this.dom.gamesList.appendChild(empty);
			return;
		}

		const fragment = document.createDocumentFragment();
		records.forEach(record => {
			fragment.appendChild(this.createGameElement(record));
		});
		this.dom.gamesList.appendChild(fragment);

		this.setupLazyIconLoading();
	}

	createGameElement(record) {
		const link = document.createElement('a');
		link.className = 'game-entry';
		link.href = record.launchUrl;
		link.setAttribute('data-game-name', record.nameLower);
		link.setAttribute('data-game-id', record.gameIdLower);
		link.setAttribute('data-game-publisher', record.companyLower);
		if (record.companyId) {
			link.setAttribute('data-company-id', record.companyId);
		}
		if (record.engineId) {
			link.setAttribute('data-engine-id', record.engineId);
		}

		const iconDiv = document.createElement('div');
		iconDiv.className = 'game-icon';

		const img = document.createElement('img');
		let iconPath = record.iconPath ? record.iconPath : null;

		if (iconPath) {
			img.setAttribute('data-src', iconPath);
			img.alt = record.name;
			img.loading = 'lazy';
			iconDiv.appendChild(img);
		} else {
			iconDiv.innerHTML = 'GAME';
			iconDiv.classList.add('no-icon');
			iconDiv.textContent = 'GAME';
		}

		const contentDiv = document.createElement('div');
		contentDiv.className = 'game-content';

		const headerDiv = document.createElement('div');
		headerDiv.className = 'game-header';

		const infoDiv = document.createElement('div');
		infoDiv.className = 'game-info';

		const titleDiv = document.createElement('div');
		titleDiv.className = 'game-title';
		titleDiv.textContent = record.name;

		const publisherDiv = document.createElement('div');
		publisherDiv.className = 'game-publisher';
		publisherDiv.textContent = this.formatPublisherText(record);

		infoDiv.appendChild(titleDiv);
		infoDiv.appendChild(publisherDiv);
		headerDiv.appendChild(infoDiv);

		const detailsDiv = document.createElement('div');
		detailsDiv.className = 'variant-details';

		if (record.platform && record.platform !== 'Unknown') {
			const platformSpan = document.createElement('span');
			platformSpan.className = 'variant-platform';
			platformSpan.title = record.platform;
			const platformIcon = this.getPlatformIcon(record.platform);
			if (platformIcon) {
				const platformImg = document.createElement('img');
				platformImg.src = platformIcon;
				platformImg.alt = record.platform;
				platformImg.title = record.platform;
				platformImg.onerror = () => {
					platformImg.style.display = 'none';
				};
				platformSpan.appendChild(platformImg);
			} else {
				const platformText = document.createElement('span');
				platformText.textContent = record.platform;
				platformSpan.appendChild(platformText);
			}
			detailsDiv.appendChild(platformSpan);
		}

		if (record.languages.length > 0) {
			const languagesSpan = document.createElement('span');
			languagesSpan.className = 'variant-languages';
			languagesSpan.title = record.languages.join(', ');

			let hasLanguageIcon = false;

			record.languages.forEach(lang => {
				const langIcon = this.getLanguageIcon(lang);
				if (!langIcon) {
					return;
				}
				const langImg = document.createElement('img');
				langImg.src = langIcon;
				langImg.alt = lang;
				langImg.title = lang.toUpperCase();
				langImg.onerror = () => {
					if (langImg.src.endsWith('.svg')) {
						langImg.src = langImg.src.replace('.svg', '.png');
					} else {
						langImg.style.display = 'none';
					}
				};
				languagesSpan.appendChild(langImg);
				hasLanguageIcon = true;
			});

			if (hasLanguageIcon) {
				detailsDiv.appendChild(languagesSpan);
			} else if (record.languages.some(lang => lang && lang !== 'Unknown')) {
				languagesSpan.textContent = record.languages.join(', ');
				detailsDiv.appendChild(languagesSpan);
			}
		}

		if (record.description) {
			const descriptionSpan = document.createElement('span');
			descriptionSpan.className = 'variant-description';
			descriptionSpan.textContent = record.description;
			detailsDiv.appendChild(descriptionSpan);
		}

		contentDiv.appendChild(headerDiv);
		if (detailsDiv.children.length > 0) {
			contentDiv.appendChild(detailsDiv);
		}

		link.appendChild(iconDiv);
		link.appendChild(contentDiv);

		return link;
	}

	setupLazyIconLoading() {
		if (!this.dom.gamesList) return;
		const lazyImages = this.dom.gamesList.querySelectorAll('.game-icon img[data-src]');
		if (lazyImages.length === 0) {
			return;
		}

		const loadImage = img => {
			const fallback = img.dataset.fallback;
			img.onerror = () => {
				if (fallback && !img.dataset.fallbackUsed) {
					img.dataset.fallbackUsed = 'true';
					img.src = fallback;
				} else {
					const wrapper = img.closest('.game-icon');
					if (wrapper) {
						wrapper.classList.add('no-icon');
						wrapper.textContent = 'GAME';
					}
					img.remove();
				}
			};
			img.src = img.getAttribute('data-src');
			img.removeAttribute('data-src');
		};

		if ('IntersectionObserver' in window) {
			const observer = new IntersectionObserver((entries, obs) => {
				entries.forEach(entry => {
					if (entry.isIntersecting) {
						loadImage(entry.target);
						obs.unobserve(entry.target);
					}
				});
			}, { rootMargin: '120px' });

			lazyImages.forEach(img => observer.observe(img));
		} else {
			lazyImages.forEach(loadImage);
		}
	}

	getPlatformIcon(platform) {
		if (!platform) {
			return null;
		}

		const platformMap = {
			'DOS': 'pc',
			'Windows': 'windows',
			'Macintosh': 'macintosh',
			'Linux': 'linux',
			'Amiga': 'amiga',
			'Amiga CD32': 'amiga',
			'Atari ST': 'atari',
			'Atari 8-bit': 'atari8',
			'Apple II': 'apple2',
			'Apple IIgs': '2gs',
			'Commodore 64': 'c64',
			'PC-98': 'pc98',
			'FM Towns': 'fmtowns',
			'Amstrad CPC': 'cpc',
			'ZX Spectrum': 'zx',
			'Acorn 32-bit': 'acorn',
			'Philips CD-i': 'cdi',
			'PlayStation': 'playstation',
			'PlayStation 2': 'playstation2',
			'Pocket PC': 'ppc',
			'Android': 'android',
			'iOS': 'ios',
			'3DO': '3do',
			'Sega Saturn': 'saturn',
			'Sega Mega Drive': 'megadrive',
			'Nintendo NES': 'nes',
			'Nintendo Wii': 'wii',
			'Xbox': 'xbox',
			'OS/2': 'os2',
			'TI-99/4A': 'ti994'
		};

		const iconName = platformMap[platform] || platform.toLowerCase().replace(/[^a-z0-9]+/g, '');
		return `data/gui-icons/icons/platforms/${iconName}.png`;
	}

	getLanguageIcon(langCode) {
		if (!langCode || langCode === 'Unknown') return null;

		const langMap = {
			'en': 'us',
			'en_GB': 'gb',
			'en_US': 'us',
			'de': 'de',
			'fr': 'fr',
			'es': 'es',
			'it': 'it',
			'nl': 'nl',
			'pl': 'pl',
			'ru': 'ru',
			'ja': 'ja',
			'ko': 'ko',
			'pt': 'pt',
			'ca': 'ca',
			'cs': 'cs',
			'da': 'da',
			'fi': 'fi',
			'he': 'he',
			'hu': 'hu',
			'nb': 'nb',
			'sv': 'se',
			'tr': 'tr',
			'zh': 'cn'
		};

		const flagCode = langMap[langCode] || langCode;
		return `data/gui-icons/icons/flags/${flagCode}.svg`;
	}

	formatPublisherText(record) {
		const hasCompany = Boolean(record.companyName);
		const hasYear = Number.isFinite(record.year);
		if (hasCompany && hasYear) {
			return `${record.companyName}, ${record.year}`;
		}
		if (hasCompany) {
			return record.companyName;
		}
		if (hasYear) {
			return String(record.year);
		}
		return 'Unknown Publisher';
	}

	showContent() {
		if (this.dom.loading) {
			this.dom.loading.style.display = 'none';
		}
		if (this.dom.error) {
			this.dom.error.style.display = 'none';
		}
		if (this.dom.content) {
			this.dom.content.style.display = 'block';
		}
	}

	showError() {
		if (this.dom.loading) {
			this.dom.loading.style.display = 'none';
		}
		if (this.dom.error) {
			this.dom.error.style.display = 'block';
		}
		if (this.dom.content) {
			this.dom.content.style.display = 'none';
		}
	}
}

document.addEventListener('DOMContentLoaded', () => {
	const heroImage = document.querySelector('.heroes');
	if (heroImage) {
		const randomIndex = Math.floor(Math.random() * 7);
		heroImage.src = `heroes${randomIndex}.png`;
	}

	new GamesLibrary();
});
