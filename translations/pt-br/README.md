<p align="center">
Traduções <br>
<a href=https://github.com/GMDSantana/crivo/tree/master/README.md>🇬🇧 EN</a>
<a href=https://github.com/GMDSantana/crivo/tree/master/translations/es/README.md>🇪🇸 ES</a>
<a href=https://github.com/GMDSantana/crivo/tree/master/translations/pt-br/README.md>🇧🇷 PT-BR</a>
<a href=https://github.com/GMDSantana/crivo/tree/master/translations/zh-cn/README.md>🇨🇳 ZH-CN</a>
 <br><br>
</p>

# Crivo

Crivo é uma ferramenta open-source em Python projetada para analistas de segurança ofensiva, pentesters e bug bounty hunters. Ela extrai e filtra URLs, IPs, domínios e subdomínios a partir de textos ou páginas da web, com capacidades integradas de web scraping. A ferramenta suporta várias opções de filtragem, escopos e configurações flexíveis de saída.

O Crivo é especialmente útil para tarefas rápidas e automação. Seu formato de saída simples e livre de informações desnecessárias o torna ideal para integração em fluxos de trabalho automatizados. Além disso, o Crivo pode processar e "filtrar" relatórios ou saídas de outras ferramentas, como o [Amass](https://github.com/owasp-amass/amass), extraindo apenas as informações relevantes e apresentando-as em uma lista limpa e organizada.

## Funcionalidades

- Extrai IPv4, IPv6, URLs, domínios e subdomínios de textos ou páginas da web.
- Aceita entrada a partir de:
  - Arquivos de texto individuais.
  - Uma lista de páginas da web em um arquivo.
  - Páginas da web individuais.
- Suporta filtragem de escopo flexível com controle detalhado sobre IPs, domínios e URLs.
- Exibe resultados diretamente no console ou salva em um arquivo especificado, mantendo a ordem dos URLs em listas.
- Oferece um modo detalhado (verbose) para informações adicionais durante a execução.

## Instalação

Certifique-se de que o Python 3.7 ou superior esteja instalado no seu sistema.

```bash
# Clone o repositório:
git clone https://github.com/GMDSantana/crivo.git

# Navegue até o diretório do projeto:
cd crivo

# Instale as dependências necessárias:
pip install -r requirements.txt
```

## Uso

Execute o Crivo pela linha de comando:

```bash
# Extrair e filtrar de um arquivo de texto:
python crivo_cli.py -f input.txt

# Buscar e filtrar de uma única página da web:
python crivo_cli.py -w https://example.com

# Buscar e filtrar de uma lista de páginas da web:
python crivo_cli.py -W webpage_list.txt

# Especificar filtros de escopo e salvar em um arquivo:
python crivo_cli.py -f input.txt -s example.com -o output.txt

# Habilitar modo detalhado para saída informativa:
python crivo_cli.py -f input.txt -v
```

### Argumentos da Linha de Comando

- `-f`, `--file`: Caminho para um arquivo de texto contendo os dados de entrada a serem filtrados.
- `-w`, `--webpage`: URL de uma única página da web para buscar e filtrar.
- `-W`, `--webpage-list`: Caminho para um arquivo de texto contendo uma lista de URLs de páginas da web para buscar e filtrar sequencialmente.
- `-o`, `--output`: Caminho para o arquivo de saída onde os resultados filtrados serão salvos. Se não especificado, os resultados serão exibidos no console.
- `-s`, `--scope`: Sequência separada por vírgulas para filtrar a saída (e.g., `ips, urls, domains`). Por padrão, todos os tipos de dados são incluídos se nenhum escopo for fornecido.
- `--ip`: Filtrar e exibir apenas endereços IP (IPv4 e IPv6).
- `--ipv4`: Filtrar e exibir apenas endereços IPv4.
- `--ipv6`: Filtrar e exibir apenas endereços IPv6.
- `--domain`: Filtrar e exibir apenas domínios e subdomínios.
- `--url`: Filtrar e exibir apenas URLs.
- `-v`, `--verbose`: Habilitar saída detalhada para mostrar informações adicionais durante a execução.
- `-V`, `--version`: Exibir a versão do programa Crivo.

## Contribuindo

Contribuições são bem-vindas! Antes de começar, leia o arquivo [CONTRIBUTING.md](CONTRIBUTING.md) para orientações sobre como contribuir de maneira eficaz. Quando estiver tudo certo, faça um fork do repositório, crie uma branch para sua funcionalidade e envie um pull request com suas alterações.

## Licença

O Crivo está licenciado sob a [Licença MIT](../LICENSE).

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

Este projeto segue a especificação [all-contributors](https://allcontributors.org).  
Contribuições de todos os tipos são bem-vindas!
