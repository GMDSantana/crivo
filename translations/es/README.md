<p align="center">
Traducciones <br>
<a href="../../README.md">🇬🇧 EN</a>
<a href="../es/README.md">🇪🇸 ES</a>
<a href="../pt-br/README.md">🇧🇷 PT-BR</a>
<a href="../zh-cn/README.md">🇨🇳 ZH-CN</a>
 <br><br>
</p>

# Crivo

Crivo es una herramienta open-source en Python diseñada para analistas de seguridad ofensiva, pentesters y bug bounty hunters. Extrae y filtra URLs, IPs, dominios y subdominios a partir de textos o páginas web, con capacidades integradas de web scraping. La herramienta admite varias opciones de filtrado, alcances y configuraciones de salida flexibles.

Crivo es especialmente útil para tareas rápidas y automatización. Su formato de salida simple y libre de información innecesaria lo hace ideal para integrarse en flujos de trabajo automatizados. Además, Crivo puede procesar y "filtrar" informes o salidas de otras herramientas, como [Amass](https://github.com/owasp-amass/amass), extrayendo solo la información relevante y presentándola en una lista limpia y organizada.

## Funcionalidades

- Extrae IPv4, IPv6 (incluidas las formas comprimidas como `2001:db8::1`), URLs, dominios y subdominios de textos o páginas web.
- Valida lo que encuentra: las IPs se comprueban octeto por octeto, y los dominios deben terminar en un dominio de nivel superior (TLD) real (lista incluida, con TLDs internacionalizados).
- Acepta entrada desde:
  - Archivos de texto individuales (en cualquier codificación; se toleran bytes no válidos).
  - La entrada estándar, para usarlo en pipelines (`cat informe.txt | crivo`).
  - Páginas web individuales.
  - Una lista de páginas web en un archivo.
- Admite filtrado de alcance flexible: por tipo de resultado, por dominio (incluidos los subdominios), por IP o rango CIDR, o por palabra clave.
- Rastreo (crawling) opcional con control de profundidad: sigue enlaces hasta la profundidad indicada, respetando el alcance (o el sitio inicial) y un límite de páginas.
- Muestra los resultados directamente en la consola o los guarda en un archivo especificado, manteniendo el orden de los URLs en las listas.
- Peticiones web robustas: tiempos de espera, reintentos automáticos ante fallos temporales, límite de tamaño, gestión de redirecciones y decodificación correcta de caracteres.
- Ofrece un modo detallado (verbose) para información adicional durante la ejecución. Los mensajes de diagnóstico van a la salida de error estándar, de modo que la salida se mantiene limpia.

## Instalación

Asegúrate de que Python 3.10 o superior esté instalado en tu sistema.

```bash
# Clona el repositorio:
git clone https://github.com/GMDSantana/crivo.git

# Navega al directorio del proyecto:
cd crivo

# Instala Crivo y sus dependencias en un entorno virtual (.venv):
scripts/install_dependencies.sh
source .venv/bin/activate
```

Como alternativa, instálalo con pip, que también proporciona el comando `crivo`:

```bash
pip install .
```

## Uso

Ejecuta Crivo desde la línea de comandos (`crivo`, `python -m crivo` o `python crivo.py`):

```bash
# Extraer y filtrar de un archivo de texto:
crivo -f input.txt

# Leer de la entrada estándar:
cat amass_output.txt | crivo --domain

# Buscar y filtrar de una sola página web (se asume https:// si no se indica esquema):
crivo -w https://example.com

# Extraer también los enlaces de los atributos href/src/action, resolviendo los relativos:
crivo -w https://example.com -r --url

# Buscar y filtrar de una lista de páginas web:
crivo -W webpage_list.txt

# Rastrear dos niveles de profundidad, sin salir de example.com y sus subdominios:
crivo -w https://example.com -c 2

# Buscar los URLs dentro del alcance encontrados en un informe y extraer también sus dominios:
crivo -f report.txt -c 1 -s example.com --domain

# Especificar filtros de alcance y guardar en un archivo:
crivo -f input.txt -s example.com -o output.txt

# Solo IPs dentro de un rango, y solo URLs de example.com o de sus subdominios:
crivo -f input.txt -s ips,10.0.0.0/8
crivo -f input.txt -s urls,*.example.com

# Habilitar modo detallado para salida informativa:
crivo -f input.txt -v
```

### Argumentos de Línea de Comando

- `-f`, `--file`: Ruta a un archivo de texto que contiene los datos de entrada a filtrar (`-` lee la entrada estándar).
- `-w`, `--webpage`: URL de una sola página web para buscar y filtrar.
- `-W`, `--webpage-list`: Ruta a un archivo de texto que contiene una lista de URLs de páginas web para buscar y filtrar secuencialmente, una por línea. Se omiten las líneas en blanco, las que empiezan por `#` y los duplicados. Cada URL se muestra antes de sus resultados.
- `-o`, `--output`: Ruta al archivo de salida donde se guardarán los resultados filtrados. Si no se especifica, los resultados se mostrarán en la consola.
- `-s`, `--scope`: Filtros de alcance separados por comas (ver más abajo). Por defecto, se incluyen todos los tipos de datos si no se proporciona un alcance.
- `--ip`: Filtra y muestra solo direcciones IP (IPv4 e IPv6).
- `--ipv4`: Filtra y muestra solo direcciones IPv4.
- `--ipv6`: Filtra y muestra solo direcciones IPv6.
- `--domain`: Filtra y muestra solo dominios y subdominios.
- `--url`: Filtra y muestra solo URLs.
- `-r`, `--resolve-links`: En páginas web, extrae también los enlaces de los atributos `href`, `src` y `action`, resolviendo los enlaces relativos a partir del URL de la página.
- `-t`, `--timeout`: Tiempo de espera de las peticiones HTTP, en segundos (por defecto: 15).
- `-k`, `--insecure`: No verifica los certificados TLS (útil en entornos de prueba con certificados autofirmados).
- `-c`, `--crawl DEPTH`: Profundidad de rastreo (por defecto: `0`, sin rastreo). Ver [Rastreo](#rastreo).
- `--max-pages N`: Número máximo de páginas que se buscan por rastreo (por defecto: `100`).
- `-v`, `--verbose`: Habilita salida detallada para mostrar información adicional durante la ejecución (en la salida de error estándar).
- `-V`, `--version`: Muestra la versión del programa Crivo.

`-f`, `-w` y `-W` son mutuamente excluyentes. Sin ninguno de ellos, Crivo lee la entrada estándar.

### Filtros de Alcance

Cada entrada de `-s`/`--scope` es una de las siguientes:

| Entrada | Significado |
| --- | --- |
| `ips`, `ipv4`, `ipv6`, `urls`, `domains`, `subdomains` | Selecciona tipos de resultado, como las opciones `--ip`, `--ipv4`, `--ipv6`, `--url` y `--domain`. `domains` y `subdomains` son equivalentes. |
| `example.com`, `*.example.com`, `https://example.com/` | Conserva `example.com` y sus subdominios, tanto como dominios como hosts de URLs. Se excluyen dominios parecidos como `notexample.com` o `example.com.evil.net`. |
| `10.0.0.5`, `10.0.0.0/8`, `2001:db8::/32` | Conserva las IPs dentro de la dirección o del rango, también como hosts de URLs. |
| cualquier otro valor, por ejemplo `admin` o `192.168.` | Una palabra clave, sin distinguir mayúsculas de minúsculas, que puede aparecer en cualquier parte del resultado. |

Las palabras clave de tipo y los objetivos se pueden combinar: `-s urls,example.com` conserva solo los URLs de `example.com` y de sus subdominios.

### Rastreo

Con `-c`/`--crawl`, Crivo sigue enlaces en anchura (breadth-first) y extrae resultados de todas las páginas que busca:

- Profundidad `0` (por defecto): sin rastreo. Crivo se comporta exactamente igual que sin `-c`.
- Profundidad `1`: Crivo también busca los URLs encontrados en la entrada inicial: los enlaces de la página indicada con `-w` (o de cada página de `-W`), o los URLs encontrados en un archivo o en la entrada estándar.
- Profundidad `2` o más: Crivo también sigue los enlaces de esas páginas, hasta la profundidad indicada.

Cómo se mantiene el rastreo bajo control:

- **El alcance se aplica en todos los niveles, incluidas las redirecciones.** Con objetivos de alcance (por ejemplo `-s example.com` o `-s 10.0.0.0/8`), solo se buscan los URLs que coinciden, y no se sigue una redirección hacia un URL fuera del alcance. Las palabras clave de tipo, como `urls`, no restringen el rastreo.
- **Sin objetivos de alcance, Crivo no sale del sitio inicial**: el host inicial (ignorando un `www.` al principio) y sus subdominios. Con un archivo o la entrada estándar, todos los URLs de la entrada se buscan en la profundidad 1, y sus hosts definen el sitio para los niveles siguientes.
- **Como máximo se buscan `--max-pages` páginas** (por defecto: 100) por rastreo, o por cada página de la lista con `-W`. Un aviso indica cuántos URLs dentro del alcance quedaron sin visitar.
- Cada página se busca una sola vez. No se buscan los enlaces a imágenes, fuentes, hojas de estilo, contenido multimedia, documentos ni archivos comprimidos, y se omiten las respuestas que no son texto; esos URLs siguen apareciendo en los resultados cuando están en una página.
- Las páginas que fallan durante el rastreo (por ejemplo, con un error 404) se notifican en un aviso y no cambian el código de salida; solo lo cambia un fallo de la página inicial.
- Los resultados de todas las páginas se reúnen en una única lista ordenada (una lista por cada página de la lista con `-W`).

### Códigos de Salida

| Código | Significado |
| --- | --- |
| `0` | Éxito (incluso cuando no se encuentra nada). |
| `1` | Se produjo un error, por ejemplo un archivo de entrada inexistente o una página que no se pudo buscar. Con `-W`, las demás páginas se siguen procesando. |
| `2` | Argumentos de línea de comandos no válidos. |
| `130` | Interrumpido con Ctrl+C. |

## Ejecutar las Pruebas

```bash
pip install -r requirements-dev.txt
pytest --cov=crivo
```

Las pruebas del web scraper usan un servidor HTTP local, por lo que no se necesita acceso a internet.

## Contribuyendo

¡Las contribuciones son bienvenidas! Antes de comenzar, lee el archivo [CONTRIBUTING.md](CONTRIBUTING.md) para obtener pautas sobre cómo contribuir de manera eficaz. Una vez que todo esté listo, haz un fork del repositorio, crea una rama para tu funcionalidad y envía un pull request con tus cambios.

## Licencia

Crivo está licenciado bajo la [Licencia MIT](../../LICENSE).

## Contributors

<!-- ALL-CONTRIBUTORS-LIST:START - Do not remove or modify this section -->
<!-- prettier-ignore-start -->
<!-- markdownlint-disable -->
<table>
  <tbody>
    <tr>
      <td align="center" valign="top" width="14.28%"><a href="https://gmdsantana.com/"><img src="https://avatars.githubusercontent.com/u/6341823?v=4?s=100" width="100px;" alt="GMDSantana"/><br /><sub><b>GMDSantana</b></sub></a><br /><a href="#code-GMDSantana" title="Code">💻</a> <a href="#design-GMDSantana" title="Design">🎨</a> <a href="#doc-GMDSantana" title="Documentation">📖</a> <a href="#test-GMDSantana" title="Tests">⚠️</a></td>
    </tr>
  </tbody>
</table>

<!-- markdownlint-restore -->
<!-- prettier-ignore-end -->

<!-- ALL-CONTRIBUTORS-LIST:END -->

Este proyecto sigue la especificación [all-contributors](https://allcontributors.org).  
¡Contribuciones de cualquier tipo son bienvenidas!
