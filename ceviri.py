# -*- coding: utf-8 -*-
"""İngilizce ve Fransızca çeviriler.

Türkçe kaynak content.py'de; burası yalnızca çeviri katmanı.

KURAL — sanat dünyasında standart olan budur:
  · Eser adları ÇEVRİLMEZ. Tablo adı bir isimdir. Türkçe kalır, altına
    küçük puntoyla çevirisi düşer.
  · Sergi ve yayın adları da isimdir; özgün hâlleriyle kalır.
    Yalnızca tanımlayıcıları çevrilir ("Kişisel sergi" → "Solo exhibition").
  · Kurum adları çevrilmez.
  · Ölçüler değişmez, yalnız santimetre (inç kaldırıldı).
"""

# ── arayüz dizgeleri ──────────────────────────────────────────────────────

UI = {
    'tr': {
        'lang_name': 'Türkçe',
        'nav_gallery': 'Galeri',
        'nav_about_grp': 'Sanatçı',
        'gal_exit': 'Ana sayfa',
        # Erişilebilir adlar: markup'a gömülüydü ve dil değişince
        # güncellenmiyordu. Kapatma düğmesinin ise hiç adı yoktu.
        'menu_open': 'Menü',
        'menu_label': 'Ana menü',
        'menu_close': 'Menüyü kapat',
        # katalog sayfasının sabit metinleri
        'gal_close': 'Kapat',
        'gal_all': 'Tümü',
        'gal_room': 'Üzerine gelin: eserin kendisi.',
        'gal_empty': 'Bu seride henüz eser yok.',
        'gal_exit_k': 'Ana sayfa',   # dar ekran kısaltmaları
        'gal_prev': 'Önceki eser', 'gal_next': 'Sonraki eser',
        'gal_works': 'Eserler',
        'hero_alt': 'Sekiz eser bir sergi salonunda, duvarlara asili.',
                'zoom_ipucu': 'Sürükleyerek gezinin · iki parmakla yakınlaştırın',
        'zoom_ipucu_fare': 'Sürükleyerek gezinin · tekerlekle yakınlaştırın',
        'zoom_baslik': 'Eseri yakından',
        'zoom_kapat': 'Kapat',
'gal_label': 'Katalog',
        'gal_title': 'Bütün eserler',
        'gal_sub': 'Bir esere tıklayınca tam ekran açılır.',
        'gal_soon': 'Bu bölüm yapım aşamasında.',
        'nav_recent': 'Son Resimler',
        'nav_studio': 'Atölye Notu',
        'nav_bio': 'Biyografi',
        'nav_exh': 'Sergiler',
        'nav_coll': 'Koleksiyonlar',
        'nav_pub': 'Yayınlar',
        'nav_press': 'Basın',
        'nav_contact': 'İletişim',
        'menu': 'Menü',
        'skip': 'İçeriğe geç',
        'site_sub': 'Resim',
        'recent_lede': '{n} eser, {s} seri. Yeniden eskiye.',
        'exh_solo': 'Kişisel Sergiler',
        'exh_group': 'Karma Sergiler',
        'coll_record': 'Kayıt',
        'coll_soon': 'Koleksiyon kayıtları hazırlanıyor.',
        'coll_sentence': '{n} eserin {h} tanesi koleksiyonlarda. Kalanlar atölyeden temin edilebilir.',
        'bio_born': '{y}’de {p}’de doğdu.',
        'bio_lives': '{c}’da yaşıyor ve çalışıyor.',
        'home_now': 'Sürüyor',
        'home_next': 'Sırada',
        'contact_body': 'Eser talepleri ve sergi önerileri için yazın.',
        'avail_studio': 'Atölyeden temin edilebilir',
        'avail_private': 'Özel koleksiyonda',
        'avail_gone': 'Ayrıldı',
        'medium': 'Tuval üzerine yağlı boya',
        # detay panelindeki künye etiketleri
        'lbl_year': 'Yıl', 'lbl_medium': 'Teknik', 'lbl_size': 'Ölçü',
        'lbl_series': 'Seri',
        # detaydaki iki kare: duz reprodüksiyon / ev ortami maketi
        'kare_eser': 'Eser', 'kare_ortam': 'Sergide',
        'noscript': 'Eserleri görüntülemek için JavaScript gerekiyor.',
        'meta_desc': 'Cemal Sağlam’ın resimleri. Tuval üzerine yağlı boya.',
    },
    'en': {
        'lang_name': 'English',
        'nav_gallery': 'Gallery',
        'nav_about_grp': 'The artist',
        'gal_exit': 'Home', 'gal_close': 'Close',
        'menu_open': 'Menu', 'menu_label': 'Main menu',
        'menu_close': 'Close menu',
        'gal_all': 'All',
        'gal_room': 'Hover: the work itself.',
        'gal_empty': 'No works in this series yet.',
        'gal_exit_k': 'Home', 
        'gal_prev': 'Previous work', 'gal_next': 'Next work',
        'gal_works': 'Works',
        'hero_alt': 'Eight paintings hung together in a gallery room.',
                'zoom_ipucu': 'Drag to pan · pinch to zoom',
        'zoom_ipucu_fare': 'Drag to pan · scroll to zoom',
        'zoom_baslik': 'Artwork close up',
        'zoom_kapat': 'Close',
'gal_label': 'Catalogue',
        'gal_title': 'All works',
        'gal_sub': 'Click a work to open it full screen.',
        'gal_soon': 'This section is under construction.',
        'nav_recent': 'Recent Paintings',
        'nav_studio': 'Studio Note',
        'nav_bio': 'Biography',
        'nav_exh': 'Exhibitions',
        'nav_coll': 'Collections',
        'nav_pub': 'Publications',
        'nav_press': 'Press',
        'nav_contact': 'Contact',
        'menu': 'Menu',
        'skip': 'Skip to content',
        'site_sub': 'Painting',
        'recent_lede': '{n} works, {s} series. Newest first.',
        'exh_solo': 'Solo Exhibitions',
        'exh_group': 'Group Exhibitions',
        'coll_record': 'Record',
        'coll_soon': 'Collection records are being prepared.',
        'coll_sentence': '{h} of {n} works are held in collections. '
                         'The remainder are available from the studio.',
        'bio_born': 'Born in {p} in {y}.',
        'bio_lives': 'Lives and works in {c}.',
        'home_now': 'Current',
        'home_next': 'Upcoming',
        'contact_body': 'For enquiries about the works and exhibition proposals, '
                        'please write.',
        'avail_studio': 'Available from the studio',
        'avail_private': 'Private collection',
        'avail_gone': 'No longer available',
        'medium': 'Oil on canvas',
        'lbl_year': 'Year', 'lbl_medium': 'Medium', 'lbl_size': 'Dimensions',
        'lbl_series': 'Series',
        'kare_eser': 'The work', 'kare_ortam': 'Installed',
        'noscript': 'JavaScript is required to view the works.',
        'meta_desc': 'Paintings by Cemal Sağlam. Oil on canvas.',
    },
    'fr': {
        'lang_name': 'Français',
        'nav_gallery': 'Galerie',
        'nav_about_grp': 'L’artiste',
        'gal_exit': 'Accueil', 'gal_close': 'Fermer',
        'menu_open': 'Menu', 'menu_label': 'Menu principal',
        'menu_close': 'Fermer le menu',
        'gal_all': 'Tout',
        'gal_room': 'Survolez : l’œuvre seule.',
        'gal_empty': 'Aucune œuvre dans cette série pour l’instant.',
        'gal_exit_k': 'Accueil', 
        'gal_prev': 'Œuvre précédente', 'gal_next': 'Œuvre suivante',
        'gal_works': 'Œuvres',
        'hero_alt': "Huit tableaux accrochés ensemble dans une"
                    " salle d'exposition.",
                'zoom_ipucu': "Faites glisser pour naviguer · pincez pour zoomer",
        'zoom_ipucu_fare': "Faites glisser pour naviguer · molette pour zoomer",
        'zoom_baslik': "L'œuvre de près",
        'zoom_kapat': 'Fermer',
'gal_label': 'Catalogue',
        'gal_title': 'Toutes les œuvres',
        'gal_sub': 'Cliquez sur une œuvre pour l’ouvrir en plein écran.',
        'gal_soon': 'Cette section est en cours de construction.',
        'nav_recent': 'Peintures récentes',
        'nav_studio': 'Note d’atelier',
        'nav_bio': 'Biographie',
        'nav_exh': 'Expositions',
        'nav_coll': 'Collections',
        'nav_pub': 'Publications',
        'nav_press': 'Presse',
        'nav_contact': 'Contact',
        'menu': 'Menu',
        'skip': 'Aller au contenu',
        'site_sub': 'Peinture',
        'recent_lede': '{n} œuvres, {s} séries. De la plus récente à la plus ancienne.',
        'exh_solo': 'Expositions personnelles',
        'exh_group': 'Expositions collectives',
        'coll_record': 'Registre',
        'coll_soon': 'Les registres de collection sont en préparation.',
        'coll_sentence': '{h} des {n} œuvres se trouvent en collection. '
                         'Les autres sont disponibles à l’atelier.',
        'bio_born': 'Né à {p} en {y}.',
        'bio_lives': 'Vit et travaille à {c}.',
        'home_now': 'En cours',
        'home_next': 'À venir',
        'contact_body': 'Pour toute demande concernant les œuvres ou une proposition '
                        'd’exposition, n’hésitez pas à écrire.',
        'avail_studio': 'Disponible à l’atelier',
        'avail_private': 'Collection privée',
        'avail_gone': 'Non disponible',
        'medium': 'Huile sur toile',
        'lbl_year': 'Année', 'lbl_medium': 'Technique', 'lbl_size': 'Dimensions',
        'lbl_series': 'Serie',
        'kare_eser': 'L’œuvre', 'kare_ortam': 'Accrochée',
        'noscript': 'JavaScript est nécessaire pour afficher les œuvres.',
        'meta_desc': 'Peintures de Cemal Sağlam. Huile sur toile.',
    },
}

# ── seriler ───────────────────────────────────────────────────────────────

SERIES = {
    # Tek gecici grup. Seri adlari ressamdan gelecek.
    'eserler': {
        'en': ('Works', ''),
        'fr': ('Œuvres', ''),
    },
}

# ── eserler: (başlık çevirisi, sanatçı notu çevirisi) ─────────────────────
# Başlık ÇEVİRİSİ gösterilir ama başlığın YERİNE geçmez — altına küçük düşer.

WORKS = {
    68784:  {'en': ('Summer Morning', 'I opened the green with yellow, not with more green.'),
             'fr': ('Matin d’été', 'J’ai ouvert le vert avec du jaune, non avec du vert.')},
    64764:  {'en': ('Morning in the Field', 'The cloud is thick, yet the light still comes through. That is the hard part.'),
             'fr': ('Matin dans les champs', 'Le nuage est épais, la lumière passe quand même. C’est là le difficile.')},
    64748:  {'en': ('Sunlit Valley', 'Distant light must be warmer than near light.'),
             'fr': ('Vallée ensoleillée', 'La lumière lointaine doit être plus chaude que la proche.')},

    64732:  {'en': ('Bearing Down', 'Finished within an hour. That rarely happens.'),
             'fr': ('L’imminence', 'Achevé en une heure. Cela arrive rarement.')},
    65353:  {'en': ('Storm', 'I worked on it through two winters. Both times in December.'),
             'fr': ('Tempête', 'J’y ai travaillé deux hivers. Les deux fois en décembre.')},
    68792:  {'en': ('The Shore', 'I painted the sea once. It came harder than land.'),
             'fr': ('Le rivage', 'J’ai peint la mer une fois. Elle est venue plus difficilement que la terre.')},

    64736:  {'en': ('Autumn Wood', 'An attempt at not explaining autumn with red.'),
             'fr': ('Bois d’automne', 'Une tentative de ne pas dire l’automne avec du rouge.')},
    69844:  {'en': ('The Lonely Farm', 'An empty house, an empty field. And yet someone seems to be there.'),
             'fr': ('La ferme isolée', 'Une maison vide, un champ vide. Et pourtant quelqu’un semble là.')},
    68388:  {'en': ('The Ridge', 'I worked without knowing what lay behind the ridge.'),
             'fr': ('La crête', 'J’ai travaillé sans savoir ce qu’il y avait derrière la crête.')},

    64772:  {'en': ('Twilight', 'The painting that gave the series its name.'),
             'fr': ('Crépuscule', 'Le tableau qui a donné son nom à la série.')},
    64724:  {'en': ('The Heron', 'The only movement on the water. I put it in last.'),
             'fr': ('Le héron', 'Le seul mouvement sur l’eau. Je l’ai mis en dernier.')},
}

# ── sanatçı sayfaları ─────────────────────────────────────────────────────
# Kurgu metinler kaldırıldı (bkz. content.py). Kaynak boşken çeviri de boş;
# gerçek metin gelince content.py ile AYNI SIRADA buraya yazılır.

BIO = {'en': [], 'fr': []}
STATEMENT = {'en': [], 'fr': []}

# ── listeler: yalnızca tanımlayıcılar çevrilir, adlar kalır ───────────────

DESCRIPTORS = {
    'Kişisel sergi': {'en': 'Solo exhibition', 'fr': 'Exposition personnelle'},
    'Karma sergi':   {'en': 'Group exhibition', 'fr': 'Exposition collective'},
}

COLLECTIONS = {'en': [], 'fr': []}

# Yayın ve basın: yalnızca açıklama / künye satırı çevrilir, sırası content.py ile aynı.
PUBLICATIONS = {'en': [], 'fr': []}
PRESS_BYLINE = {'en': [], 'fr': []}
