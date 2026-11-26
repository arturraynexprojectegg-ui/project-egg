# Техническая спецификация концептов логотипа

Прочитай также `../BRIEF.md`.

## Файлы
- Папка стиля: `logos/<NN-style>/`
- 10 логотипов: `01.svg` … `10.svg`
- `meta.json`: массив из 10 объектов `{"file":"01.svg","title":"<короткое название на русском>","concept":"<1–2 предложения на русском: идея, почему подходит Primeegg>","colors":["#hex",...],"fonts":["..."]}`

## Формат SVG
- `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 300">`, без width/height, без фона (прозрачный) — карточка галереи светлая (#FAF7F2).
- Логотип по центру, поля ≥ 24px со всех сторон.
- Только чистый SVG: path, circle, ellipse, rect, polygon, line, text, g, defs, linearGradient/radialGradient, clipPath, mask. Без <image>, без внешних ссылок, без <style> с @import, без скриптов, без filter (тени не нужны).
- Шрифты: используй `font-family` ТОЛЬКО из списка ниже (галерея грузит их из Google Fonts), всегда с fallback, например `font-family="Fraunces, serif"`. Указывай font-weight явно.
  - Serif: Fraunces, Playfair Display, DM Serif Display, Cormorant Garamond, Libre Baskerville, Abril Fatface, Lora
  - Sans: Montserrat, Manrope, Space Grotesk, Syne, Bricolage Grotesque, Outfit, Archivo Black, Josefin Sans, Bebas Neue, Oswald, Inter
  - Rounded/friendly: Fredoka, Baloo 2, Nunito, Quicksand
  - Script/display: Pacifico, Lobster, Caveat, Yellowtail, Rye
- Текст бренда: «PRIMEEGG» или «Primeegg» (одно слово; можно визуально разделить Prime|egg цветом/весом). Дескриптор по желанию: «DISTRIBUTION», «Farm Eggs & Egg Products», «Huevos · Ovoproductos», «ESPAÑA».
- Знак (иконка) должен быть самостоятельным и читаться в 32px.
- Каждый из 10 логотипов в стиле должен быть ЗАМЕТНО другим: другая идея знака, другая композиция (горизонтальная / вертикальная / эмблема / только wordmark), другая палитра. Не делай 10 перекрасок одного.
- Рисуй аккуратно: проверяй геометрию (форма яйца — не эллипс, а асимметричная: уже сверху. Хороший path яйца в боксе 100×130 с центром (50,65): `M50 0 C78 0 100 45 100 80 C100 110 78 130 50 130 C22 130 0 110 0 80 C0 45 22 0 50 0 Z`), текст не должен вылезать за viewBox и не должен налезать на знак. Для ширины текста ориентируйся: заглавные ~0.65–0.75 × font-size на символ для широких sans, ~0.55 для узких.

## Проверка
- После записи прогони `xmllint --noout logos/<NN-style>/*.svg` (должно быть без ошибок) и `python3 -c "import json;json.load(open('logos/<NN-style>/meta.json'))"`.
- Не трогай файлы вне своей папки. Не делай git-коммиты.
