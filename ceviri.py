# -*- coding: utf-8 -*-
"""İngilizce ve Fransızca çeviriler.

Türkçe kaynak content.py'de; burası yalnızca çeviri katmanı.

KURAL — sanat dünyasında standart olan budur:
  · Eser adları ÇEVRİLMEZ. Tablo adı bir isimdir. Türkçe kalır, altına
    küçük puntoyla çevirisi düşer.
  · Sergi ve yayın adları da isimdir; özgün hâlleriyle kalır.
    Yalnızca tanımlayıcıları çevrilir ("Kişisel sergi" → "Solo exhibition").
  · Kurum adları çevrilmez.
  · Ölçüler değişmez: metrik önce, inç parantezde.
"""

# ── arayüz dizgeleri ──────────────────────────────────────────────────────

UI = {
    'tr': {
        'lang_name': 'Türkçe',
        'nav_gallery': 'Galeri',
        'nav_about_grp': 'Sanatçı',
        'gal_exit': 'Galeriden çık',
        # galeri sayfasının sabit metinleri
        'gal_top': 'Başa dön', 'gal_close': 'Kapat',
        'gal_exit_k': 'Çık', 'gal_top_k': 'Başa',   # dar ekran kısaltmaları
        'gal_prev': 'Önceki eser', 'gal_next': 'Sonraki eser',
        'gal_works': 'Eserler',
        'gal_hint': 'Kaydırarak duvar boyunca ilerleyin · tabloya tıklayın',
        'gal_hint_touch': 'Sağa sola kaydırın · tabloya dokunun',
        'gal_label': 'Sergi duvarı',
        'gal_title': 'Galeriye gir',
        'gal_sub': 'Eserler bir Fransız salonunun duvarında, gerçek santimetre ölçeğinde asılı. '
                    'Duvar boyunca ilerleyin; bir tabloya tıklayınca tam ekran açılır.',
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
        'coll_sentence': '{n} eserin {h} tanesi koleksiyonlarda. Kalanlar atölyeden temin edilebilir.',
        'bio_born': '{y}’de {p}’de doğdu.',
        'bio_lives': '{c}’da yaşıyor ve çalışıyor.',
        'home_now': 'Sürüyor',
        'home_next': 'Sırada',
        'contact_body': 'Eser talepleri, atölye ziyareti ve sergi önerileri için yazın. '
                        'Atölye ziyaretleri randevuyla.',
        'avail_studio': 'Atölyeden temin edilebilir, İstanbul',
        'avail_private': 'Özel koleksiyonda',
        'avail_gone': 'Ayrıldı',
        'medium': 'Tuval üzerine yağlı boya',
        # detay panelindeki künye etiketleri
        'lbl_year': 'Yıl', 'lbl_medium': 'Teknik', 'lbl_size': 'Ölçü',
        'lbl_series': 'Seri',
        'noscript': 'Eserleri görüntülemek için JavaScript gerekiyor.',
        'meta_desc': 'Cemal Sağlam, İstanbul’da çalışan ressam. Tuval üzerine yağlı boya; '
                     'alacakaranlık, hava ve manzara üzerine seriler.',
    },
    'en': {
        'lang_name': 'English',
        'nav_gallery': 'Gallery',
        'nav_about_grp': 'The artist',
        'gal_exit': 'Leave the gallery',
        'gal_top': 'Back to start', 'gal_close': 'Close',
        'gal_exit_k': 'Exit', 'gal_top_k': 'Start',
        'gal_prev': 'Previous work', 'gal_next': 'Next work',
        'gal_works': 'Works',
        'gal_hint': 'Scroll to move along the wall · click a painting',
        'gal_hint_touch': 'Swipe left or right · tap a painting',
        'gal_label': 'The exhibition wall',
        'gal_title': 'Enter the gallery',
        'gal_sub': 'The works hang on the wall of a French salon at true centimetre scale. '
                    'Move along the wall; click a painting to open it full screen.',
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
        'coll_sentence': '{h} of {n} works are held in collections. '
                         'The remainder are available from the studio.',
        'bio_born': 'Born in {p} in {y}.',
        'bio_lives': 'Lives and works in {c}.',
        'home_now': 'Current',
        'home_next': 'Upcoming',
        'contact_body': 'For enquiries about available work, studio visits and exhibition '
                        'proposals, please write. Studio visits by appointment.',
        'avail_studio': 'Available from the studio, Istanbul',
        'avail_private': 'Private collection',
        'avail_gone': 'No longer available',
        'medium': 'Oil on canvas',
        'lbl_year': 'Year', 'lbl_medium': 'Medium', 'lbl_size': 'Dimensions',
        'lbl_series': 'Series',
        'noscript': 'JavaScript is required to view the works.',
        'meta_desc': 'Cemal Sağlam is a painter working in Istanbul. Oil on canvas; series on '
                     'twilight, weather and landscape.',
    },
    'fr': {
        'lang_name': 'Français',
        'nav_gallery': 'Galerie',
        'nav_about_grp': 'L’artiste',
        'gal_exit': 'Quitter la galerie',
        'gal_top': 'Retour au début', 'gal_close': 'Fermer',
        'gal_exit_k': 'Sortir', 'gal_top_k': 'Début',
        'gal_prev': 'Œuvre précédente', 'gal_next': 'Œuvre suivante',
        'gal_works': 'Œuvres',
        'gal_hint': 'Faites défiler pour avancer le long du mur · cliquez sur un tableau',
        'gal_hint_touch': 'Balayez à gauche ou à droite · touchez un tableau',
        'gal_label': 'Le mur d’exposition',
        'gal_title': 'Entrer dans la galerie',
        'gal_sub': 'Les œuvres sont accrochées au mur d’un salon français à l’échelle réelle. '
                    'Avancez le long du mur ; cliquez sur un tableau pour l’ouvrir en plein écran.',
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
        'coll_sentence': '{h} des {n} œuvres se trouvent en collection. '
                         'Les autres sont disponibles à l’atelier.',
        'bio_born': 'Né à {p} en {y}.',
        'bio_lives': 'Vit et travaille à {c}.',
        'home_now': 'En cours',
        'home_next': 'À venir',
        'contact_body': 'Pour toute demande concernant les œuvres disponibles, les visites '
                        'd’atelier et les propositions d’exposition, écrivez-nous. '
                        'Visites d’atelier sur rendez-vous.',
        'avail_studio': 'Disponible à l’atelier, Istanbul',
        'avail_private': 'Collection privée',
        'avail_gone': 'Non disponible',
        'medium': 'Huile sur toile',
        'lbl_year': 'Année', 'lbl_medium': 'Technique', 'lbl_size': 'Dimensions',
        'lbl_series': 'Série',
        'noscript': 'JavaScript est nécessaire pour afficher les œuvres.',
        'meta_desc': 'Cemal Sağlam est un peintre établi à Istanbul. Huile sur toile ; séries '
                     'sur le crépuscule, le temps et le paysage.',
    },
}

# ── seriler ───────────────────────────────────────────────────────────────

SERIES = {
    'alacakaranlik': {
        'en': ('Twilight',
               'Paintings of the short interval when the day has ended and night has not begun. '
               'Colour here does not describe something; it holds something disappearing.'),
        'fr': ('Crépuscule',
               'Peintures de ce bref intervalle où le jour s’achève et où la nuit n’a pas '
               'commencé. La couleur n’y décrit rien ; elle retient ce qui disparaît.'),
    },
    'hava': {
        'en': ('Weather',
               'Storm, rain, pressure. The atmosphere itself rather than the landscape. '
               'I put the air on the canvas first, the ground after.'),
        'fr': ('Temps',
               'Orage, pluie, pression. L’atmosphère elle-même plutôt que le paysage. '
               'Je pose l’air sur la toile d’abord, le sol ensuite.'),
    },
    'topografya': {
        'en': ('Quiet Topography',
               'Land without people. Places where no one is present but someone clearly passed.'),
        'fr': ('Topographie silencieuse',
               'Des terres sans personne. Des lieux où nul n’est présent mais où quelqu’un '
               'est manifestement passé.'),
    },
    'sabah': {
        'en': ('Morning',
               'The silver light series. The first half hour of morning, before colour settles.'),
        'fr': ('Matin',
               'La série de la lumière d’argent. La première demi-heure du matin, '
               'avant que la couleur ne se fixe.'),
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

# ── biyografi ─────────────────────────────────────────────────────────────

BIO = {
    'en': [
        'He completed the painting department at Mimar Sinan Fine Arts University, then spent '
        'two years in Vienna studying classical oil technique.',
        'He says he chose oil for its slowness. He works on a single canvas for months, leaves '
        'the layers to dry and returns to them. Most of the work is waiting.',
        'Since 2016 he has painted in his studio in Bomonti, Istanbul. His work is held in '
        'private collections in Turkey, Austria and the Netherlands.',
    ],
    'fr': [
        'Il est diplômé du département de peinture de '
        'l’université des beaux-arts Mimar Sinan, puis a passé deux ans à Vienne à étudier les '
        'techniques classiques de la peinture à l’huile.',
        'Il dit avoir choisi l’huile pour sa lenteur. Il travaille des mois sur une même toile, '
        'laisse sécher les couches, y revient. L’essentiel du travail consiste à attendre.',
        'Depuis 2016 il peint dans son atelier de Bomonti, à Istanbul. Ses œuvres figurent dans '
        'des collections privées en Turquie, en Autriche et aux Pays-Bas.',
    ],
}

STATEMENT = {
    'en': [
        'When I begin a canvas I do not know what it will look like. I only know which light I '
        'am after: the half hour when the day has ended and night has not yet come. Until I find '
        'it, I keep covering the surface over.',
        'Colour shifts as the layers dry, so it cannot be hurried. I spend about four months on a '
        'painting, and perhaps a third of that is actually spent applying paint. The rest is '
        'looking and waiting.',
        'I do not think I paint landscapes. The landscape is a pretext; what matters is the '
        'weight of the air. A storm has a colour, and the aftermath of rain has another. '
        'I am trying to describe those.',
    ],
    'fr': [
        'Quand je commence une toile, je ne sais pas à quoi elle ressemblera. Je sais seulement '
        'quelle lumière je cherche : la demi-heure où le jour s’achève et où la nuit n’est pas '
        'encore venue. Jusqu’à la trouver, je recouvre.',
        'La couleur change à mesure que les couches sèchent : on ne peut donc pas se presser. '
        'Je passe environ quatre mois sur un tableau, et le tiers peut-être de ce temps à poser '
        'de la peinture. Le reste, à regarder et à attendre.',
        'Je ne crois pas peindre des paysages. Le paysage est un prétexte ; ce qui compte est le '
        'poids de l’air. Un orage a une couleur, l’après-pluie en a une autre. '
        'J’essaie de les décrire.',
    ],
}

# ── listeler: yalnızca tanımlayıcılar çevrilir, adlar kalır ───────────────

DESCRIPTORS = {
    'Kişisel sergi': {'en': 'Solo exhibition', 'fr': 'Exposition personnelle'},
    'Karma sergi':   {'en': 'Group exhibition', 'fr': 'Exposition collective'},
}

COLLECTIONS = {
    'en': [
        'Ardıç Sanat Collection, Istanbul',
        'Batı Kanat Contemporary Art Collection, Istanbul',
        'Liman Cultural Centre, İzmir',
        'Atelier Nordbahn Collection, Vienna',
        'Van Doorn Collection, Rotterdam',
        'Private collections · Turkey, Austria, the Netherlands',
    ],
    'fr': [
        'Collection Ardıç Sanat, Istanbul',
        'Collection d’art contemporain Batı Kanat, Istanbul',
        'Centre culturel Liman, İzmir',
        'Collection Atelier Nordbahn, Vienne',
        'Collection Van Doorn, Rotterdam',
        'Collections privées · Turquie, Autriche, Pays-Bas',
    ],
}

PUBLICATIONS = {
    'en': [
        'Exhibition catalogue, 96 pp. Text: Nihal Erkut. Ardıç Sanat.',
        'Exhibition catalogue, 64 pp. Payas Galeri.',
        'Interview · Sanat Dünyamız, issue 189, pp. 44–51.',
        'Exhibition catalogue, 72 pp. Text: Kaan Bilen. Ardıç Sanat.',
        'Essay · Kunstraum Yearbook, Vienna. In German and English.',
    ],
    'fr': [
        'Catalogue d’exposition, 96 p. Texte : Nihal Erkut. Ardıç Sanat.',
        'Catalogue d’exposition, 64 p. Payas Galeri.',
        'Entretien · Sanat Dünyamız, n° 189, p. 44–51.',
        'Catalogue d’exposition, 72 p. Texte : Kaan Bilen. Ardıç Sanat.',
        'Essai · Annuaire du Kunstraum, Vienne. En allemand et en anglais.',
    ],
}

# Basın: yazı başlıkları Türkçe yayınlarda çıktı, özgün hâlleriyle kalıyor.
# Yalnızca ay adları çevriliyor.
PRESS_BYLINE = {
    'en': [
        'Ayşe Tunca · Cumhuriyet Kitap, November 2024',
        'Deniz Aksoy · Argonotlar, October 2024',
        'Selim Arer · Sanat Dünyamız, March 2023',
        'Kaan Bilen · e-skop, December 2021',
    ],
    'fr': [
        'Ayşe Tunca · Cumhuriyet Kitap, novembre 2024',
        'Deniz Aksoy · Argonotlar, octobre 2024',
        'Selim Arer · Sanat Dünyamız, mars 2023',
        'Kaan Bilen · e-skop, décembre 2021',
    ],
}

NOTICE = {
    'en': 'This is a design prototype. The artist identity and all texts are fictional; the '
          'images are public-domain paintings by George Inness from the Art Institute of '
          'Chicago open-access archive. All will be replaced with the artist’s own work '
          'before launch.',
    'fr': 'Ceci est un prototype de conception. L’identité de l’artiste et les textes sont '
          'fictifs ; les images sont des tableaux de George Inness du domaine public, issus '
          'des archives en libre accès de l’Art Institute of Chicago. Tout sera remplacé par '
          'les œuvres de l’artiste avant la mise en ligne.',
}
