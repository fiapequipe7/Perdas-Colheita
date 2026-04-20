# FIAP - Faculdade de Informática e Administração Paulista

<p align="center">
<a href= "https://www.fiap.com.br/"><img src="assets/logo-fiap.png" alt="FIAP - Faculdade de Informática e Administração Paulista" border="0" width=40% height=40%></a>
</p>

<br>

# Sistema de Monitoramento de Colheita de Cana-de-Açúcar

## Nome do grupo

Equipe 7

## 👨‍🎓 Integrantes:

* <a href="#">Luiz Henrique Martins Dias</a>
* <a href="#">Ricardo Colpani Sprocati de OLiveira</a>
* <a href="#">Walter Corradini Ferreira</a>
* <a href="#">Fahd Ozelame Al Khaldi</a>
* <a href="#">Eric Roberto Miglioli</a>

## 👩‍🏫 Professores:

### Tutor(a)

* <a href="#">Nicolly Candida Rodrigues de Souza</a>

### Coordenador(a)

* <a href="#">Andre Godoi Chiovato</a>

---

## 📜 Descrição

O agronegócio é um dos pilares fundamentais da economia brasileira, sendo responsável por grande parte da produção de alimentos, geração de empregos e desenvolvimento econômico. Dentro desse contexto, a produção de cana-de-açúcar se destaca, porém enfrenta desafios significativos relacionados à perda de produtividade durante o processo de colheita.

Estudos indicam que perdas na colheita mecanizada podem chegar a até 15% da produção, impactando diretamente o lucro do produtor e a eficiência do setor. Diante desse problema, o presente projeto propõe o desenvolvimento de um sistema simples de monitoramento de colheitas, com o objetivo de auxiliar no controle e análise dessas perdas.

A solução desenvolvida permite ao usuário registrar colheitas por talhão, calcular automaticamente a produção esperada, identificar a perda percentual e classificá-la em níveis (baixa, moderada ou alta). Além disso, o sistema gera resumos operacionais, armazena dados em arquivos JSON e permite o envio das informações para um banco de dados Oracle, garantindo persistência e rastreabilidade.

O projeto aplica conceitos fundamentais da linguagem Python, incluindo funções, estruturas de dados (listas, dicionários e tuplas), manipulação de arquivos (texto e JSON) e integração com banco de dados. A interface foi desenvolvida via terminal, priorizando clareza e usabilidade, mesmo em ambiente de linha de comando.

Dessa forma, o sistema contribui para a tomada de decisão do produtor rural, oferecendo uma visão mais clara sobre o desempenho da colheita e possibilitando a identificação de problemas operacionais que afetam a produtividade.

---

## 📁 Estrutura de pastas

Dentre os arquivos e pastas presentes na raiz do projeto, definem-se:

* <b>.github</b>: Arquivos de configuração do GitHub.

* <b>assets</b>: Contém imagens utilizadas no README.

* <b>scripts</b>: Contém scripts auxiliares, como o `schema_oracle.sql` para criação da tabela no banco de dados.

* <b>src</b>: Contém todo o código-fonte do sistema:

  * `main.py`: ponto de entrada do sistema
  * `ui.py`: interface com o usuário (menu e interação)
  * `servicos.py`: regras de negócio
  * `db_oracle.py`: conexão com banco Oracle
  * `dados/`: arquivos JSON e TXT utilizados pelo sistema

* <b>README.md</b>: Documento principal com descrição do projeto.

---

## 🔧 Como executar o código

### Pré-requisitos

* Python 3.10 ou superior
* Biblioteca Oracle:

```bash
pip install oracledb
```

Ou utilizando o arquivo:

```bash
pip install -r requirements.txt
```

---

### Passo a passo

1. Clone o repositório:

```bash
git clone <link-do-repositorio>
```

2. Acesse a pasta do projeto:

```bash
cd projeto
```

3. Execute o sistema:

```bash
python src/main.py
```

---

### Banco de dados Oracle (opcional)

Caso deseje criar a tabela manualmente:

* Utilize o script disponível em:

```
scripts/schema_oracle.sql
```

---

## 🗃 Histórico de lançamentos

* 0.2.0 - 20/04/2026

  * Reestruturação das pastas e módulos do projeto

* 0.1.0 - 14/04/2026

  * Estrutura inicial do projeto

---

## 📋 Licença

<img style="height:22px!important;margin-left:3px;vertical-align:text-bottom;" src="https://mirrors.creativecommons.org/presskit/icons/cc.svg?ref=chooser-v1">
<img style="height:22px!important;margin-left:3px;vertical-align:text-bottom;" src="https://mirrors.creativecommons.org/presskit/icons/by.svg?ref=chooser-v1">

<p xmlns:cc="http://creativecommons.org/ns#" xmlns:dct="http://purl.org/dc/terms/">
<a property="dct:title" rel="cc:attributionURL" href="https://github.com/agodoi/template">MODELO GIT FIAP</a> por 
<a rel="cc:attributionURL dct:creator" property="cc:attributionName" href="https://fiap.com.br">Fiap</a> está licenciado sobre 
<a href="http://creativecommons.org/licenses/by/4.0/?ref=chooser-v1" target="_blank" rel="license noopener noreferrer">
Attribution 4.0 International
</a>.
</p>
