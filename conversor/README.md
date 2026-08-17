# Conversor de monedas Takenos

Prototipo de un conversor de monedas (landing + calculadora) para Takenos, construido como un único archivo HTML autocontenido (fuentes, banderas y logo embebidos en base64 — sin dependencias externas).

## Estructura

- `build.py` — genera `conversor-takenos.html` a partir de las plantillas y los assets en `assets/`.
- `assets/` — fuentes (Space Grotesk, Fragment Mono), logos (blanco/violeta) y banderas (extraídas de la librería de Figma "Brand-design" de Takenos), más la imagen de fondo del hero.
- `conversor-takenos.html` — salida generada, lista para publicar como Artifact o servir como página estática.

## Regenerar el HTML

```bash
cd conversor
python3 build.py
```

Requiere `Pillow`, `numpy` y `scipy` solo si se vuelve a procesar una imagen nueva (recorte de fondo transparente); para simplemente regenerar el HTML con los assets ya existentes no son necesarios.

## Datos

- Las tasas (`CURRENCIES` en `build.py`) son un snapshot estático de `https://app.takenos.com/api/rates?currency=ALL` — esa API no acepta CORS desde ningún origin salvo `app.takenos.com`, así que no se puede fetchear en vivo desde el navegador.
- El historial de tipo de cambio (sección "Historial") usa datos reales de Snowflake (`TAKENOS_DWH.SRC.SRC_TAKENOS_PRODUCTION_RATE`), pero solo ARS y BOB tienen series diarias completas; el resto de las monedas no tiene historial logueado.

## Pendiente / ideas abiertas

- El título y subtítulo del hero cambian dinámicamente según la moneda seleccionada en la calculadora.
- Falta el whitelisting de CORS en el backend de Takenos si en algún momento se quiere hacer fetch en vivo desde el dominio final donde se publique esto.
