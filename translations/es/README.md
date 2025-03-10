<p align="center">
Traducciones <br>
<a href=https://github.com/GMDSantana/crivo/tree/master/README.md>🇬🇧 EN</a>
<a href=https://github.com/GMDSantana/crivo/tree/master/translations/es/README.md>🇪🇸 ES</a>
<a href=https://github.com/GMDSantana/crivo/tree/master/translations/pt-br/README.md>🇧🇷 PT-BR</a>
<a href=https://github.com/GMDSantana/crivo/tree/master/translations/zh-cn/README.md>🇨🇳 ZH-CN</a>
 <br><br>
</p>

# Crivo

Crivo es una herramienta open-source en Python diseñada para analistas de seguridad ofensiva, pentesters y bug bounty hunters. Extrae y filtra URLs, IPs, dominios y subdominios a partir de textos o páginas web, con capacidades integradas de web scraping. La herramienta admite varias opciones de filtrado, alcances y configuraciones de salida flexibles.

Crivo es especialmente útil para tareas rápidas y automatización. Su formato de salida simple y libre de información innecesaria lo hace ideal para integrarse en flujos de trabajo automatizados. Además, Crivo puede procesar y "filtrar" informes o salidas de otras herramientas, como [Amass](https://github.com/owasp-amass/amass), extrayendo solo la información relevante y presentándola en una lista limpia y organizada.

## Funcionalidades

- Extrae IPv4, IPv6, URLs, dominios y subdominios de textos o páginas web.
- Acepta entrada desde:
  - Archivos de texto individuales.
  - Una lista de páginas web en un archivo.
  - Páginas web individuales.
- Admite filtrado de alcance flexible con control detallado sobre IPs, dominios y URLs.
- Muestra los resultados directamente en la consola o los guarda en un archivo especificado, manteniendo el orden de los URLs en las listas.
- Ofrece un modo detallado (verbose) para información adicional durante la ejecución.

## Instalación

Asegúrate de que Python 3.7 o superior esté instalado en tu sistema.

```bash
# Clona el repositorio:
git clone https://github.com/GMDSantana/crivo.git

# Navega al directorio del proyecto:
cd crivo

# Instala las dependencias necesarias:
pip install -r requirements.txt
```

## Uso

Ejecuta Crivo desde la línea de comandos:

```bash
# Extraer y filtrar de un archivo de texto:
python  crivo.py -f input.txt

# Buscar y filtrar de una sola página web:
python  crivo.py -w https://example.com

# Buscar y filtrar de una lista de páginas web:
python  crivo.py -W webpage_list.txt

# Especificar filtros de alcance y guardar en un archivo:
python  crivo.py -f input.txt -s example.com -o output.txt

# Habilitar modo detallado para salida informativa:
python  crivo.py -f input.txt -v
```

### Argumentos de Línea de Comando

- `-f`, `--file`: Ruta a un archivo de texto que contiene los datos de entrada a filtrar.
- `-w`, `--webpage`: URL de una sola página web para buscar y filtrar.
- `-W`, `--webpage-list`: Ruta a un archivo de texto que contiene una lista de URLs de páginas web para buscar y filtrar secuencialmente.
- `-o`, `--output`: Ruta al archivo de salida donde se guardarán los resultados filtrados. Si no se especifica, los resultados se mostrarán en la consola.
- `-s`, `--scope`: Secuencia separada por comas para filtrar la salida (e.g., `ips, urls, domains`). Por defecto, se incluyen todos los tipos de datos si no se proporciona un alcance.
- `--ip`: Filtra y muestra solo direcciones IP (IPv4 e IPv6).
- `--ipv4`: Filtra y muestra solo direcciones IPv4.
- `--ipv6`: Filtra y muestra solo direcciones IPv6.
- `--domain`: Filtra y muestra solo dominios y subdominios.
- `--url`: Filtra y muestra solo URLs.
- `-v`, `--verbose`: Habilita salida detallada para mostrar información adicional durante la ejecución.
- `-V`, `--version`: Muestra la versión del programa Crivo.

## Contribuyendo

¡Las contribuciones son bienvenidas! Antes de comenzar, lee el archivo [CONTRIBUTING.md](CONTRIBUTING.md) para obtener pautas sobre cómo contribuir de manera eficaz. Una vez que todo esté listo, haz un fork del repositorio, crea una rama para tu funcionalidad y envía un pull request con tus cambios.

## Licencia

Crivo está licenciado bajo la [Licencia MIT](../LICENSE).

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
