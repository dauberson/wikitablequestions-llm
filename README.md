# wikitablequestions-llm

Projeto para explorar o dataset do wikipedia chamado [WikiTableQuestions](https://ppasupat.github.io/WikiTableQuestions/).
Para acessar os dados, existem duas opções, além de baixar pela interface do site.
- Instando o pacote **datasets**
  - pip install datasets
  - os dados ja vem separados em bases de treino, teste e validação
- Usando o comando bash wget e unzip
  - wget "https://github.com/ppasupat/WikiTableQuestions/releases/download/v1.0.2/WikiTableQuestions-1.0.2-compact.zip" -O data.zip
  - unzip -o data.zip

O dataset é organizado em alguns diretórios contendo varios datasets sobre diversos contextos, o dado pode ser encontrado no formato .html, .csv ou .tsv. 
Para esse projeto vamos usa os arquivos .csv e o diretório com identificador 200.

Tabela ./csv/200-csv/0.csv

| Year | Title                          | Chart-Positions UK | Chart-Positions US | Chart-Positions NL | Comments                                                                             |
|------|--------------------------------|--------------------|--------------------|--------------------|--------------------------------------------------------------------------------------|
| 1969 | Renaissance                    | 60                 | –                  | 10                 |                                                                                      |
| 1971 | Illusion                       | –                  | –                  | –                  | 1976 (UK)                                                                            |
| 1972 | Prologue                       | –                  | –                  | –                  |                                                                                      |
| 1973 | Ashes Are Burning              | –                  | 171                | –                  |                                                                                      |
| 1974 | Turn of the Cards              | –                  | 94                 | –                  | 1975 (UK)                                                                            |
| 1975 | Scheherazade and Other Stories | –                  | 48                 | –                  |                                                                                      |
| 1977 | Novella                        | –                  | 46                 | –                  | 1977 (January in US, August in UK, as the band moved to the Warner Bros Music Group) |
| 1978 | A Song for All Seasons         | 35                 | 58                 | –                  | UK:Silver                                                                            |
| 1979 | Azure d'Or                     | 73                 | 125                | –                  |                                                                                      |
| 1981 | Camera Camera                  | –                  | 196                | –                  |                                                                                      |
| 1983 | Time-Line                      | –                  | 207                | –                  |                                                                                      |
| 2001 | Tuscany                        | –                  | –                  | –                  |                                                                                      |
| 2013 | Grandine il Vento              | –                  | –                  | –                  |                                                                                      |

Foi usado uma função para percorrer o diretório 200 e adicionando cada dataframe em uma lista: [dataframes.py](wikitablequestions-llm-service-core%2Fmain%2Fwikitablequestions_llm_service_core%2Fhandlers%2Fdataframes.py)

Como os dataframes são de contextos diferentes, foi usado a LLM para obter algumas informações sobre o contexto de cada dataframe, isso auxiliara para armazenar o dado no banco de dados.

O template do prompt para extrair essas informações foi o seguinte:

```python
prompt_template_str = """\
Give me a Summary and Table Name of the table below with the following JSON format

- The table name must be unique to the table and describe it while being concise.
- Do NOT output a generic table name (e.g. table, my_table).
- Do NOT make the table name one of the following: {exclude_table_name_list}

Table:
{table_str}
"""
```
Foi criado duas funções: [extract_wikitables_infos.py](wikitablequestions-llm-service-core%2Fmain%2Fwikitablequestions_llm_service_core%2Fhandlers%2Fextract_wikitables_infos.py), uma para verificar se o dataframe ja tem informações extraidas para evitar consumo excessivo de requisicoes na API do OpenAI, caso exista é retornado as informações que estão armazenadas no diretório [WikiTableQuestions_Infos](wikitablequestions-llm-service-core%2Fmain%2Fwikitablequestions_llm_service_core%2Fdata%2FWikiTableQuestions_Infos), e outra para fazer as requisições das informações de cada tabela.

Os resultados podem foram salvos em .json e podem ser vistos no diretório: [WikiTableQuestions_Infos](wikitablequestions-llm-service-core%2Fmain%2Fwikitablequestions_llm_service_core%2Fdata%2FWikiTableQuestions_Infos)

Para configurar e setar os modelos de llm e embedding foi usado as funções: [llm_model_handler.py](wikitablequestions-llm-service-core%2Fmain%2Fwikitablequestions_llm_service_core%2Fmodels_handlers%2Fllm_model_handler.py) e [embed_model_handler.py](wikitablequestions-llm-service-core%2Fmain%2Fwikitablequestions_llm_service_core%2Fmodels_handlers%2Fembed_model_handler.py).
Como a aplicação foi executado localmente e no Cloud Run(com poucos recursos), foi escolhido o modelo da OpenAI para otimizar esse gasto de recursos de máquina.

Pontos relevantes dessa parte do fluxo é que foi usado uma configuração de output das interações com o modelo de LLM evitando alucinações e controlando melhor a qualidade do resultado, isso foi configurado usando o parametro ```output_cls```  da função ```LLMTextCompletionProgram.from_defaults()```. 
Essa configuração permite receber uma classe BaseModel do Pydantic que consegue parsear o output e criar uma instancia dessa classe, tudo isso porque é inserido informações dessa classe no template do prompt.

```python
from pydantic import BaseModel, Field


class TableInfo(BaseModel):
    """Information regarding a structured table."""

    table_name: str = Field(
        ..., description="table name (must be underscores and NO spaces)"
    )
    summary: str = Field(
        ..., description="short, concise summary/caption of the table"
    )

```

Essa informações foram utilizadas como metadados das tabelas de cada .csv, foi usado o `sqlalchemy` para construir essa parte do fluxo.
Para entender melhor como essas tabelas foram criadas: [create_sql_tables.py](wikitablequestions-llm-service-core%2Fmain%2Fwikitablequestions_llm_service_core%2Fhandlers%2Fcreate_sql_tables.py)

Tudo é válido somente em tempo de execução, sendo alocado em memória, por se tratar de um caso de experimentação. Então, ao reiniciar a aplicação, boa parte é processada novamente.



### Infraestrutura

- É usado o Github Actions para CI/CD, toda configuração pode ser vista pelo arquivo: [main_workflow.yaml](.github%2Fworkflows%2Fmain_workflow.yaml)
  - O pipeline tem 4 steps:
    - Build (Baseada no [pyproject.toml](pyproject.toml))
    - Release
    - Publicar o Pacote Python
    - Build Imagem Docker
    
- Foi usado a GCP como Cloud para armazenar os pacotes python e imagens docker.
  - Para provisionar todos serviços, apis e configurações na GCP foi usado IaC, Terraform. Os arquivos podem ser vistos no diretório: [google-cloud-infrastructure-tf](google-cloud-infrastructure-tf)
    - Configurações iniciais como ativar apis e criar bucket para salvar os states do terraform: [google-basics-to-init](google-cloud-infrastructure-tf%2Fgoogle-basics-to-init) 
    - Criação dos repositórios Python e Docker: [google-artifact-registry-repository](google-cloud-infrastructure-tf%2Fgoogle-artifact-registry-repository)
    - Configuração para o Github Actions conseguir interagir com a GCP via OIDC/WIP: [google-github-actions](google-cloud-infrastructure-tf%2Fgoogle-github-actions)

- Para servir o que foi construido, foi usado FastAPI para conseguir fazer requisições na aplicação, passando as perguntas e obetendo as respostas. Tudo isso esta rodando usando o serviço Cloud Run da GCP.
  - Pode ser visto pelo link: 

### TO-DO;

- Construir uma interface user friendly, como streamlit para o usuário passar os textos por ela, ao inves de usar o swagger.
- Configurar o arize-phoenix para ter observabilidade da performance das tasks de LLM
- Conseguir usar/carregar dentro da aplicação modelos open-source
  - Como foi usando o Cloud Run para deployar a aplicação, o recurso era limitado, então foi usado a LLM do OpenAI.
- Usar um banco para salvar os dados e indexes ao inves de salvar tudo em memória
