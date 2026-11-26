"""Строки интерфейса логобуков и брендбуков: русский исходник -> uk / es.
L(s) переводит строку на текущий язык (set_lang). Неизвестная строка возвращается как есть
и попадает в MISSING — сборщик печатает их в конце, чтобы ничего не осталось по-русски."""
import re

LANG = "ru"
MISSING = set()
LANG_NAMES = {"uk": "Українська", "es": "Español"}


def set_lang(lang):
    global LANG
    LANG = lang


S = {
    # ---- общие
    "ЛОГОБУК": ("ЛОГОБУК", "MANUAL DE LOGOTIPO"),
    "БРЕНДБУК": ("БРЕНДБУК", "MANUAL DE MARCA"),
    "Обложка": ("Обкладинка", "Portada"),
    "Финал": ("Фінал", "Cierre"),
    # ---- логобук
    "Концепция": ("Концепція", "Concepto"),
    "ЭЛЕМЕНТЫ ЗНАКА": ("ЕЛЕМЕНТИ ЗНАКА", "ELEMENTOS DEL SÍMBOLO"),
    "Основной логотип": ("Основний логотип", "Logotipo principal"),
    "Основная версия логотипа. Используется по умолчанию на всех носителях, где позволяет место и фон.":
        ("Основна версія логотипа. Використовується за замовчуванням на всіх носіях, де дозволяють місце й фон.",
         "Versión principal del logotipo. Se usa por defecto en todos los soportes donde el espacio y el fondo lo permiten."),
    "Версии логотипа": ("Версії логотипа", "Versiones del logotipo"),
    "Версии": ("Версії", "Versiones"),
    "Горизонтальная": ("Горизонтальна", "Horizontal"),
    "Вертикальная": ("Вертикальна", "Vertical"),
    "Знак": ("Знак", "Símbolo"),
    "Надпись": ("Напис", "Logotipo tipográfico"),
    "Шапка сайта, накладные, борт фургона": ("Шапка сайту, накладні, борт фургона", "Cabecera web, albaranes, lateral de furgoneta"),
    "Упаковка, стенды, квадратные форматы": ("Упаковка, стенди, квадратні формати", "Envases, expositores, formatos cuadrados"),
    "Иконка, фавикон, штамп на яйце, соцсети": ("Іконка, фавікон, штамп на яйці, соцмережі", "Icono, favicon, sello en el huevo, redes sociales"),
    "Узкие форматы, текстовые упоминания": ("Вузькі формати, текстові згадки", "Formatos estrechos, menciones en texto"),
    "Охранное поле": ("Охоронне поле", "Área de protección"),
    "ОХРАННОЕ ПОЛЕ": ("ОХОРОННЕ ПОЛЕ", "ÁREA DE PROTECCIÓN"),
    "В охранное поле не заходят текст, края носителя, другие логотипы и активные элементы фона. При увеличении логотипа поле масштабируется пропорционально.":
        ("В охоронне поле не заходять текст, краї носія, інші логотипи й активні елементи фону. Під час збільшення логотипа поле масштабується пропорційно.",
         "En el área de protección no entran textos, bordes del soporte, otros logotipos ni elementos activos del fondo. Al ampliar el logotipo, el área crece en proporción."),
    "Минимальный размер": ("Мінімальний розмір", "Tamaño mínimo"),
    "ОСНОВНОЙ ЛОГОТИП": ("ОСНОВНИЙ ЛОГОТИП", "LOGOTIPO PRINCIPAL"),
    "ЗНАК": ("ЗНАК", "SÍMBOLO"),
    "Фирменные цвета": ("Фірмові кольори", "Colores corporativos"),
    "Цвета": ("Кольори", "Colores"),
    "Цветовые версии": ("Колірні версії", "Versiones de color"),
    "Цветная на светлом фоне": ("Кольорова на світлому тлі", "A color sobre fondo claro"),
    "Цветная на тёмном фоне": ("Кольорова на темному тлі", "A color sobre fondo oscuro"),
    "Одноцветная чёрная": ("Одноколірна чорна", "Monocromo negro"),
    "Одноцветная белая на тёмном": ("Одноколірна біла на темному", "Monocromo blanco sobre oscuro"),
    "Белая на фирменном цвете": ("Біла на фірмовому кольорі", "Blanco sobre color corporativo"),
    "Фирменный цвет на светлом": ("Фірмовий колір на світлому", "Color corporativo sobre claro"),
    "Типографика": ("Типографіка", "Tipografía"),
    "Начертания: ": ("Накреслення: ", "Pesos: "),
    "Недопустимое использование": ("Неприпустиме використання", "Usos incorrectos"),
    "Не растягивать и не сжимать": ("Не розтягувати й не стискати", "No estirar ni comprimir"),
    "Не поворачивать": ("Не повертати", "No girar"),
    "Не перекрашивать в чужие цвета": ("Не перефарбовувати в чужі кольори", "No cambiar a colores ajenos"),
    "Не ставить на фон с низким контрастом": ("Не ставити на тло з низьким контрастом", "No usar sobre fondos de bajo contraste"),
    "Не размещать на пёстром фоне": ("Не розміщувати на строкатому тлі", "No colocar sobre fondos recargados"),
    "Не обрезать и не выводить за край": ("Не обрізати й не виводити за край", "No recortar ni sacar del borde"),
    "Знак в цифровой среде": ("Знак у цифровому середовищі", "El símbolo en entornos digitales"),
    "ИКОНКА ПРИЛОЖЕНИЯ": ("ІКОНКА ЗАСТОСУНКУ", "ICONO DE APLICACIÓN"),
    "Скругление 22% от стороны, знак занимает ~75% площади.": ("Заокруглення 22% від сторони, знак займає ~75% площі.", "Radio del 22 % del lado; el símbolo ocupa ~75 % del área."),
    "АВАТАР СОЦСЕТЕЙ": ("АВАТАР СОЦМЕРЕЖ", "AVATAR EN REDES"),
    "Круглая маска: знак вписан с полем 15%.": ("Кругла маска: знак вписано з полем 15%.", "Máscara circular: el símbolo con un margen del 15 %."),
    "ФАВИКОН": ("ФАВІКОН", "FAVICON"),
    "Знак работает самостоятельно там, где название уже прочитано из контекста: иконки, фавиконы, штамп на скорлупе, пломбы и наклейки на таре. В остальных случаях используется полный логотип.":
        ("Знак працює самостійно там, де назву вже зчитано з контексту: іконки, фавікони, штамп на шкаралупі, пломби й наліпки на тарі. В інших випадках використовується повний логотип.",
         "El símbolo funciona solo cuando el nombre ya se lee por el contexto: iconos, favicons, sello en la cáscara, precintos y etiquetas en cajas. En el resto de casos se usa el logotipo completo."),
    # ---- брендбук
    "Платформа бренда": ("Платформа бренду", "Plataforma de marca"),
    "Суть бренда": ("Суть бренду", "Esencia de marca"),
    "Миссия": ("Місія", "Misión"),
    "Видение": ("Бачення", "Visión"),
    "Позиционирование": ("Позиціонування", "Posicionamiento"),
    "Ценности": ("Цінності", "Valores"),
    "Аудитория": ("Аудиторія", "Público"),
    "ЧТО ВАЖНО": ("ЩО ВАЖЛИВО", "QUÉ LE IMPORTA"),
    "ЧТО МЫ ГОВОРИМ": ("ЩО МИ КАЖЕМО", "QUÉ LE DECIMOS"),
    "Характер": ("Характер", "Personalidad"),
    "Характер и голос": ("Характер і голос", "Personalidad y tono"),
    "Принципы голоса": ("Принципи голосу", "Principios del tono"),
    "Так говорим": ("Так говоримо", "Así hablamos"),
    "Так не говорим": ("Так не говоримо", "Así no hablamos"),
    "Слоганы": ("Слогани", "Eslóganes"),
    "Слоганы и заголовки": ("Слогани й заголовки", "Eslóganes y titulares"),
    "ГЛАВНЫЙ СЛОГАН · ES": ("ГОЛОВНИЙ СЛОГАН · ES", "ESLOGAN PRINCIPAL · ES"),
    "Заголовки для коммуникаций": ("Заголовки для комунікацій", "Titulares para comunicación"),
    "Логотип": ("Логотип", "Logotipo"),
    "Цвет": ("Колір", "Color"),
    "Пропорции цвета в коммуникациях": ("Пропорції кольору в комунікаціях", "Proporciones de color en la comunicación"),
    "Основной цвет держит узнаваемость, акцент — только для выделения (цена, новинка, кнопка). Нейтральные цвета дают воздух и работают фоном для продукта.":
        ("Основний колір тримає впізнаваність, акцент — лише для виділення (ціна, новинка, кнопка). Нейтральні кольори дають простір і працюють тлом для продукту.",
         "El color principal sostiene el reconocimiento; el de acento solo destaca (precio, novedad, botón). Los neutros dan aire y sirven de fondo al producto."),
    "Типографическая иерархия": ("Типографічна ієрархія", "Jerarquía tipográfica"),
    "Лид · 28 / 40": ("Лід · 28 / 40", "Entradilla · 28 / 40"),
    "Текст · 18 / 28": ("Текст · 18 / 28", "Texto · 18 / 28"),
    "Подпись · 13 / 18": ("Підпис · 13 / 18", "Pie · 13 / 18"),
    "Графический элемент": ("Графічний елемент", "Elemento gráfico"),
    "Фирменный паттерн": ("Фірмовий патерн", "Patrón corporativo"),
    "Паттерн — фон, а не герой: под логотипом и текстом на нём всегда есть спокойная плашка. Масштаб — не мельче, чем 1/12 ширины носителя.":
        ("Патерн — тло, а не герой: під логотипом і текстом на ньому завжди є спокійна плашка. Масштаб — не дрібніше ніж 1/12 ширини носія.",
         "El patrón es fondo, no protagonista: bajo el logotipo y los textos siempre hay una placa lisa. Escala mínima: 1/12 del ancho del soporte."),
    "Фотостиль": ("Фотостиль", "Estilo fotográfico"),
    "ФОТО": ("ФОТО", "FOTO"),
    # ---- сцены мокапов
    "Пиктограммы": ("Піктограми", "Pictogramas"),
    "Восемь линейных пиктограмм на сетке 64 px с единой толщиной линии и скруглениями — для сайта, упаковки, презентаций и навигации.":
        ("Вісім лінійних піктограм на сітці 64 px з єдиною товщиною лінії та заокругленнями — для сайту, упаковки, презентацій і навігації.",
         "Ocho pictogramas lineales en retícula de 64 px, con grosor de trazo y redondeos uniformes, para web, envases, presentaciones y señalética."),
    "Упаковка для розницы": ("Упаковка для роздрібу", "Envases para retail"),
    "Коробки на 6 и 12 яиц из формованной целлюлозы с фирменной этикеткой и яйца со штампом знака и кодом производителя ЕС.":
        ("Коробки на 6 і 12 яєць із формованої целюлози з фірмовою етикеткою та яйця зі штампом знака й кодом виробника ЄС.",
         "Estuches de 6 y 12 huevos de celulosa moldeada con faja corporativa, y huevos con el sello del símbolo y el código de productor de la UE."),
    "HoReCa и оптовые поставки": ("HoReCa та оптові поставки", "Hostelería y venta mayorista"),
    "Лоток на 30 яиц с фирменной бумажной обечайкой и гофроящик на 360 яиц (12 лотков) с одноцветной флексопечатью, манипуляционными знаками и транспортной этикеткой.":
        ("Лоток на 30 яєць із фірмовою паперовою обгорткою та гофроящик на 360 яєць (12 лотків) з одноколірним флексодруком, маніпуляційними знаками й транспортною етикеткою.",
         "Bandeja de 30 huevos con faja de papel corporativa y caja de cartón ondulado para 360 huevos (12 bandejas) con flexografía a una tinta, pictogramas de manipulación y etiqueta logística."),
    "Яичный порошок": ("Яєчний порошок", "Huevo en polvo"),
    "Крафт-мешок 25 кг с прошитым верхом и одноцветной печатью спецификации и розничный дой-пак 500 г с окном в форме яйца.":
        ("Крафт-мішок 25 кг із прошитим верхом і одноколірним друком специфікації та роздрібний дой-пак 500 г з віконцем у формі яйця.",
         "Saco kraft de 25 kg con cierre cosido y ficha técnica impresa a una tinta, y doypack de 500 g para retail con ventana en forma de huevo."),
    "Логистика": ("Логістика", "Logística"),
    "Рефрижераторный фургон в фирменной ливрее и паллета с коробами под стрейч-плёнкой с транспортной этикеткой.":
        ("Рефрижераторний фургон у фірмовій ліврії та палета з коробами під стрейч-плівкою з транспортною етикеткою.",
         "Furgoneta frigorífica con la rotulación corporativa y palé de cajas con film estirable y etiqueta logística."),
    "Деловая документация": ("Ділова документація", "Papelería corporativa"),
    "Фирменный бланк и счёт-фактура A4, конверты DL и визитки сотрудника — лицо с паттерном и оборот с контактами.":
        ("Фірмовий бланк і рахунок-фактура A4, конверти DL та візитки співробітника — лице з патерном і зворот із контактами.",
         "Carta y factura A4, sobres DL y tarjetas de visita: anverso con el patrón y reverso con los datos de contacto."),
    "Униформа": ("Уніформа", "Uniformes"),
    "Поло с вышитым логотипом, фартук с нагрудником и карманом для персонала HoReCa и склада, бейсболка со знаком.":
        ("Поло з вишитим логотипом, фартух із нагрудником і кишенею для персоналу HoReCa та складу, бейсболка зі знаком.",
         "Polo con logotipo bordado, delantal con peto y bolsillo para el personal de hostelería y almacén, y gorra con el símbolo."),
    "Сайт": ("Сайт", "Sitio web"),
    "Главная страница primeegg.es: шапка с меню, hero в фирменном цвете с иллюстрацией и карточки продуктов — на десктопе и в мобильной версии.":
        ("Головна сторінка primeegg.es: шапка з меню, hero у фірмовому кольорі з ілюстрацією та картки продуктів — на десктопі й у мобільній версії.",
         "Página de inicio de primeegg.es: cabecera con menú, hero en el color corporativo con ilustración y fichas de producto, en escritorio y en móvil."),
    "Социальные сети": ("Соціальні мережі", "Redes sociales"),
    "Профиль @primeegg в Instagram и три шаблона постов: заголовок на фирменном цвете, паттерн со знаком и карточка продукта.":
        ("Профіль @primeegg в Instagram і три шаблони постів: заголовок на фірмовому кольорі, патерн зі знаком і картка продукту.",
         "Perfil @primeegg en Instagram y tres plantillas de publicación: titular sobre el color corporativo, patrón con el símbolo y ficha de producto."),
    "Для кириллицы: ": ("Для кирилиці: ", "Para cirílico: "),

}

P = [  # (регулярка по русскому, uk-шаблон, es-шаблон)
    (r"^PRIMEEGG · (ЛОГОБУК|БРЕНДБУК) · (.+)$", "PRIMEEGG · {T1} · \\2", "PRIMEEGG · {T1} · \\2"),
    (r"^PRIMEEGG · ЛОГОБУК (\S+) · (.+)$", "PRIMEEGG · ЛОГОБУК \\1 · \\2", "PRIMEEGG · MANUAL DE LOGOTIPO \\1 · \\2"),
    (r"^PRIMEEGG · БРЕНДБУК (\S+) · (.+)$", "PRIMEEGG · БРЕНДБУК \\1 · \\2", "PRIMEEGG · MANUAL DE MARCA \\1 · \\2"),
    (r"^Концепт (\S+) · версия 1\.0 · (.+)$", "Концепт \\1 · версія 1.0 · \\2", "Concepto \\1 · versión 1.0 · \\2"),
    (r"^Фирменный стиль · версия 1\.0 · (.+)$", "Фірмовий стиль · версія 1.0 · \\1", "Identidad corporativa · versión 1.0 · \\1"),
    (r"^Логобук (\S+) · (.+) · версия 1\.0 · (.+)$", "Логобук \\1 · \\2 · версія 1.0 · \\3", "Manual de logotipo \\1 · \\2 · versión 1.0 · \\3"),
    (r"^Primeegg Distribution SL · Брендбук (\S+) · версия 1\.0 · (.+)$", "Primeegg Distribution SL · Брендбук \\1 · версія 1.0 · \\2",
     "Primeegg Distribution SL · Manual de marca \\1 · versión 1.0 · \\2"),
    (r"^Минимальное свободное пространство вокруг логотипа равно 1x, где x — (.+)\.$",
     "Мінімальний вільний простір навколо логотипа дорівнює 1x, де x — \\1.",
     "El espacio libre mínimo alrededor del logotipo es 1x, donde x es \\1."),
    (r"^мин\. (\d+) px$", "мін. \\1 px", "mín. \\1 px"),
    (r"^Печать: ширина не менее (\d+) мм\. Экран: не менее (\d+) px\.$",
     "Друк: ширина не менше \\1 мм. Екран: не менше \\2 px.", "Impresión: ancho mínimo \\1 mm. Pantalla: mínimo \\2 px."),
    (r"^Минимум для знака: (\d+) px \(фавикон\)\.$", "Мінімум для знака: \\1 px (фавікон).", "Mínimo para el símbolo: \\1 px (favicon)."),
    (r"^Полные правила использования логотипа — в логобуке (\S+)\.$", "Повні правила використання логотипа — у логобуці \\1.",
     "Las normas completas de uso del logotipo están en el manual de logotipo \\1."),
    (r"^СЕГМЕНТ (\d+)$", "СЕГМЕНТ \\1", "SEGMENTO \\1"),
    (r"^Шрифты: (.+)\. Все — Google Fonts, свободная лицензия\.$", "Шрифти: \\1. Усі — Google Fonts, вільна ліцензія.",
     "Tipografías: \\1. Todas de Google Fonts, licencia libre."),
    (r"^(\d\d) (.+)$", "\\1 {T2}", "\\1 {T2}"),
]


def L(s):
    if LANG == "ru" or not isinstance(s, str):
        return s
    i = 0 if LANG == "uk" else 1
    if s in S:
        return S[s][i]
    for rx, uk, es in P:
        m = re.match(rx, s)
        if m:
            out = m.expand((uk, es)[i])
            if "{T1}" in out:
                out = out.replace("{T1}", L(m.group(1)))
            if "{T2}" in out:
                out = out.replace("{T2}", L(m.group(2)))
            return out
    if re.search(r"[А-Яа-яЁё]", s):
        MISSING.add(s)
    return s
