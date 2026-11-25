<p align="center">
Traduções <br>
<a href="../../README.md">🇬🇧 EN</a>
<a href="../es/README.md">🇪🇸 ES</a>
<a href="../pt-br/README.md">🇧🇷 PT-BR</a>
<a href="../zh-cn/README.md">🇨🇳 ZH-CN</a>
 <br><br>
</p>

# Crivo

Crivo é uma ferramenta open-source em Python projetada para analistas de segurança ofensiva, pentesters e bug bounty hunters. Ela extrai e filtra URLs, IPs, domínios e subdomínios a partir de textos ou páginas da web, com capacidades integradas de web scraping. A ferramenta suporta várias opções de filtragem, escopos e configurações flexíveis de saída.

O Crivo é especialmente útil para tarefas rápidas e automação. Seu formato de saída simples e livre de informações desnecessárias o torna ideal para integração em fluxos de trabalho automatizados. Além disso, o Crivo pode processar e "filtrar" relatórios ou saídas de outras ferramentas, como o [Amass](https://github.com/owasp-amass/amass), extraindo apenas as informações relevantes e apresentando-as em uma lista limpa e organizada.

## Funcionalidades

- Extrai IPv4, IPv6 (incluindo formas comprimidas como `2001:db8::1`), URLs, domínios e subdomínios de textos ou páginas da web.
- Valida o que encontra: os IPs são verificados octeto por octeto, e os domínios precisam terminar em um domínio de topo (TLD) real (lista incluída, com TLDs internacionalizados).
- Aceita entrada a partir de:
  - Arquivos de texto individuais (em qualquer codificação; bytes inválidos são tolerados).
  - Entrada padrão, para uso em pipelines (`cat relatorio.txt | crivo`).
  - Páginas da web individuais.
  - Uma lista de páginas da web em um arquivo.
- Suporta filtragem de escopo flexível: por tipo de resultado, por domínio (incluindo subdomínios), por IP ou faixa CIDR, ou por palavra-chave.
- Rastreamento (crawling) opcional com controle de profundidade: segue links até a profundidade indicada, respeitando o escopo (ou o site inicial) e um limite de páginas.
- Exibe resultados diretamente no console ou salva em um arquivo especificado, mantendo a ordem dos URLs em listas.
- Requisições web robustas: timeouts, novas tentativas automáticas em falhas temporárias, limite de tamanho, tratamento de redirecionamentos e decodificação correta de caracteres.
- Oferece um modo detalhado (verbose) para informações adicionais durante a execução. As mensagens de diagnóstico vão para a saída de erro padrão, mantendo a saída limpa.

## Instalação

Certifique-se de que o Python 3.10 ou superior esteja instalado no seu sistema.

```bash
# Clone o repositório:
git clone https://github.com/GMDSantana/crivo.git

# Navegue até o diretório do projeto:
cd crivo

# Instale o Crivo e suas dependências em um ambiente virtual (.venv):
scripts/install_dependencies.sh
source .venv/bin/activate
```

Como alternativa, instale com o pip, que também disponibiliza o comando `crivo`:

```bash
pip install .
```

## Uso

Execute o Crivo pela linha de comando (`crivo`, `python -m crivo` ou `python crivo.py`):

```bash
# Extrair e filtrar de um arquivo de texto:
crivo -f input.txt

# Ler da entrada padrão:
cat amass_output.txt | crivo --domain

# Buscar e filtrar de uma única página da web (https:// é assumido se nenhum esquema for informado):
crivo -w https://example.com

# Extrair também os links dos atributos href/src/action, resolvendo os relativos:
crivo -w https://example.com -r --url

# Buscar e filtrar de uma lista de páginas da web:
crivo -W webpage_list.txt

# Rastrear dois níveis de profundidade, permanecendo em example.com e seus subdomínios:
crivo -w https://example.com -c 2

# Buscar os URLs dentro do escopo encontrados em um relatório e extrair domínios deles também:
crivo -f report.txt -c 1 -s example.com --domain

# Especificar filtros de escopo e salvar em um arquivo:
crivo -f input.txt -s example.com -o output.txt

# Apenas IPs dentro de uma faixa, e apenas URLs de example.com ou de seus subdomínios:
crivo -f input.txt -s ips,10.0.0.0/8
crivo -f input.txt -s urls,*.example.com

# Habilitar modo detalhado para saída informativa:
crivo -f input.txt -v
```

### Argumentos da Linha de Comando

- `-f`, `--file`: Caminho para um arquivo de texto contendo os dados de entrada a serem filtrados (`-` lê a entrada padrão).
- `-w`, `--webpage`: URL de uma única página da web para buscar e filtrar.
- `-W`, `--webpage-list`: Caminho para um arquivo de texto contendo uma lista de URLs de páginas da web para buscar e filtrar sequencialmente, um por linha. Linhas em branco, linhas iniciadas por `#` e duplicatas são ignoradas. Cada URL é exibido antes dos seus resultados.
- `-o`, `--output`: Caminho para o arquivo de saída onde os resultados filtrados serão salvos. Se não especificado, os resultados serão exibidos no console.
- `-s`, `--scope`: Filtros de escopo separados por vírgulas (veja abaixo). Por padrão, todos os tipos de dados são incluídos se nenhum escopo for fornecido.
- `--ip`: Filtrar e exibir apenas endereços IP (IPv4 e IPv6).
- `--ipv4`: Filtrar e exibir apenas endereços IPv4.
- `--ipv6`: Filtrar e exibir apenas endereços IPv6.
- `--domain`: Filtrar e exibir apenas domínios e subdomínios.
- `--url`: Filtrar e exibir apenas URLs.
- `-r`, `--resolve-links`: Para páginas da web, extrair também os links dos atributos `href`, `src` e `action`, resolvendo links relativos a partir do URL da página.
- `-t`, `--timeout`: Tempo limite das requisições HTTP, em segundos (padrão: 15).
- `-k`, `--insecure`: Não verificar certificados TLS (útil em ambientes de teste com certificados autoassinados).
- `-c`, `--crawl DEPTH`: Profundidade de rastreamento (padrão: `0`, sem rastreamento). Veja [Rastreamento](#rastreamento).
- `--max-pages N`: Número máximo de páginas buscadas por rastreamento (padrão: `100`).
- `-v`, `--verbose`: Habilitar saída detalhada para mostrar informações adicionais durante a execução (na saída de erro padrão).
- `-V`, `--version`: Exibir a versão do programa Crivo.

`-f`, `-w` e `-W` são mutuamente exclusivos. Sem nenhum deles, o Crivo lê a entrada padrão.

### Filtros de Escopo

Cada entrada de `-s`/`--scope` é uma das seguintes:

| Entrada | Significado |
| --- | --- |
| `ips`, `ipv4`, `ipv6`, `urls`, `domains`, `subdomains` | Seleciona tipos de resultado, como as opções `--ip`, `--ipv4`, `--ipv6`, `--url` e `--domain`. `domains` e `subdomains` são equivalentes. |
| `example.com`, `*.example.com`, `https://example.com/` | Mantém `example.com` e seus subdomínios, tanto como domínios quanto como hosts de URLs. Domínios parecidos, como `notexample.com` ou `example.com.evil.net`, são excluídos. |
| `10.0.0.5`, `10.0.0.0/8`, `2001:db8::/32` | Mantém os IPs dentro do endereço ou da faixa, inclusive como hosts de URLs. |
| qualquer outro valor, por exemplo `admin` ou `192.168.` | Uma palavra-chave, sem diferenciar maiúsculas de minúsculas, que pode aparecer em qualquer parte do resultado. |

Palavras-chave de tipo e alvos podem ser combinados: `-s urls,example.com` mantém apenas os URLs de `example.com` e de seus subdomínios.

### Rastreamento

Com `-c`/`--crawl`, o Crivo segue links em largura (breadth-first) e extrai resultados de todas as páginas que busca:

- Profundidade `0` (padrão): sem rastreamento. O Crivo se comporta exatamente como sem `-c`.
- Profundidade `1`: o Crivo também busca os URLs encontrados na entrada inicial: os links da página informada com `-w` (ou de cada página de `-W`), ou os URLs encontrados em um arquivo ou na entrada padrão.
- Profundidade `2` ou mais: o Crivo também segue os links dessas páginas, até a profundidade indicada.

Como o rastreamento é mantido sob controle:

- **O escopo é aplicado em todos os níveis, inclusive em redirecionamentos.** Com alvos de escopo (por exemplo `-s example.com` ou `-s 10.0.0.0/8`), apenas os URLs correspondentes são buscados, e um redirecionamento para um URL fora do escopo não é seguido. Palavras-chave de tipo, como `urls`, não restringem o rastreamento.
- **Sem alvos de escopo, o Crivo permanece no site inicial**: o host inicial (ignorando um `www.` no início) e seus subdomínios. Com um arquivo ou a entrada padrão, todos os URLs da entrada são buscados na profundidade 1, e os hosts deles definem o site para os níveis seguintes.
- **No máximo `--max-pages` páginas** (padrão: 100) são buscadas por rastreamento, ou por página listada com `-W`. Um aviso informa quantos URLs dentro do escopo ficaram sem visita.
- Cada página é buscada apenas uma vez. Links para imagens, fontes, folhas de estilo, mídia, documentos e arquivos compactados não são buscados, e respostas que não são texto são ignoradas; esses URLs continuam aparecendo nos resultados quando estão em uma página.
- Páginas que falham durante o rastreamento (por exemplo, com erro 404) são relatadas em um aviso e não alteram o código de saída; apenas uma falha na página inicial o altera.
- Os resultados de todas as páginas são reunidos em uma única lista ordenada (uma lista por página listada com `-W`).

### Códigos de Saída

| Código | Significado |
| --- | --- |
| `0` | Sucesso (inclusive quando nada é encontrado). |
| `1` | Ocorreu um erro, por exemplo um arquivo de entrada inexistente ou uma página que não pôde ser buscada. Com `-W`, as demais páginas ainda são processadas. |
| `2` | Argumentos de linha de comando inválidos. |
| `130` | Interrompido com Ctrl+C. |

## Executando os Testes

```bash
pip install -r requirements-dev.txt
pytest --cov=crivo
```

Os testes do web scraper usam um servidor HTTP local, portanto não é necessário acesso à internet.

## Contribuindo

Contribuições são bem-vindas! Antes de começar, leia o arquivo [CONTRIBUTING.md](CONTRIBUTING.md) para orientações sobre como contribuir de maneira eficaz. Quando estiver tudo certo, faça um fork do repositório, crie uma branch para sua funcionalidade e envie um pull request com suas alterações.

## Licença

O Crivo está licenciado sob a [Licença MIT](../../LICENSE).

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
