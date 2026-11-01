# Художественный ориентир v14

Создан встроенным инструментом `image_gen` (навык `imagegen`), 31 октября
2026. Результат: [art-direction.png](art-direction.png), прозрачный фон.

Это визуальный референс для композиции, силуэтов и освещения. Игровые
спрайты нарисованы отдельно в нативном размере: 16×32 и 16×16. Референс
не уменьшался и не квантовался для получения игровых PNG.

Рабочие карты: [pixels.json](pixels.json). Итог в проекте:
`assets/Crops/herbalCrops.png`, `assets/Items/herbalItems.png`.

## Полный промпт

```text
Use case: stylized-concept. Asset type: a single concept contact sheet for four medicinal crop sprites in a Stardew Valley pixel art mod. This is an ART DIRECTION reference, for later manual drawing at 16x32 pixels per plant, NOT a painted illustration to downsample. Create four mature crop plants side by side with clear separation on transparent background, no typography, no labels, no grid, no shadows on ground. Strongly simplified chunky NATIVE LOW RESOLUTION PIXEL ART: each plant should visibly have approximately only 14 logical pixels width by 29 logical pixels height; show each logical pixel as a crisp large square at identical integer zoom, no subpixel texture or anti-aliasing. Art direction: lush, charming, artistic, vibrant, juicy, strong volume, large sweeping curved leaves with readable pointed shapes, very large harvest parts, concentrated warm highlights and cool deep shadows, dark colored outlines. Asymmetric organic silhouettes and elegant S curved stems. Plants fill most of their 16x32 cell width, broad leaves splay out sideways, fruit occupy a substantial part of the upper canopy; avoid a thin straight stem with three identical balls arranged vertically. From left to right: (1) Glass Dewberry: emerald and spring-green serrated leaves, three fat rich BLUE round berries with bright cyan and tiny pale blue highlights, overlapping slightly on curved stems. (2) Moonvelvet: broad arcing sage and vivid green leaves with visible veins, three large drooping lavender/violet BELL-shaped flowers with glossy pink highlights, dark plum interiors, flared petals. (3) Amber Heartleaf: red curved stems, large lush green leaves and three large GOLDEN HEART-shaped harvest LEAVES with central veins, warm yellow highlight and copper shadow. Heartleaf has NO berries and NO flowers. (4) Silver Seamleaf: sweeping emerald/mint lance leaves with pale veins, two large distinct IVORY five petal flowers with golden centers and one closed ivory bud. Keep every silhouette botanical and readable. No tiny scattered dots, no dainty sparse plants, no muted matte palette, no smooth vector gradients, no realism, no pots. Artistic handmade game sprites with bold highlights and lush broad leaf masses.
```
