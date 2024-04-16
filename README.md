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

Foi usado uma função para percorrer o diretório 200 e adicionando cada dataframe em uma lista:


```python
import logging
from pathlib import Path
from typing import Optional, List

import pandas as pd


def get_dataframes(csv_id: int) -> Optional[List[pd.DataFrame]]:
    data_dir = Path(f"./data/WikiTableQuestions/csv/{csv_id}-csv")
    csv_files = sorted([f for f in data_dir.glob("*.csv")])
    dataframes_list = []
    for csv_file in csv_files:
        logging.info(f"processing file: {csv_file}")
        try:
            df = pd.read_csv(csv_file)
            dataframes_list.append(df)
        except Exception as e:
            logging.error(f"Error parsing {csv_file}: {e}")
            continue
    return dataframes_list
```

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

Para configurar e setar os modelos de llm e embedding foi usado as seguintes funções, como os códigos foram executados localmente e isso exige recursos, foi escolhido o modelo da OpenAI.

```python
from llama_index.core import Settings
import logging

import torch
from llama_index.core.callbacks import LlamaDebugHandler, CallbackManager
from llama_index.llms.huggingface import HuggingFaceLLM
from llama_index.embeddings.huggingface import HuggingFaceEmbedding


def get_llm(
        model_name: str = None,
        tokenizer_name: str = None,
        context_window: int = None,
        max_new_tokens: int = None,
        temperature: float = None
):
    if not context_window:
        context_window = 2048

    if not max_new_tokens:
        max_new_tokens = 256

    if not temperature:
        temperature = 0.5

    if not model_name:
        logging.warning("Model not setted, will use default model")
        model_name = "TheBloke/Llama-2-13B-chat-GPTQ"
        
    if not tokenizer_name:
        if model_name:
            tokenizer_name = model_name
        else:
            tokenizer_name = "TheBloke/Llama-2-13B-chat-GPTQ"

    llama_debug = LlamaDebugHandler(print_trace_on_end=True)
    callback_manager = CallbackManager([llama_debug])

    return HuggingFaceLLM(
        context_window=context_window,
        max_new_tokens=max_new_tokens,
        generate_kwargs={"temperature": temperature, "do_sample": True},
        tokenizer_name=tokenizer_name,
        model_name=model_name,
        device_map="auto",
        callback_manager=callback_manager,
        tokenizer_kwargs={"max_length": 4096},
        # change these settings below depending on your GPU
        # model_kwargs={"torch_dtype": torch.float16, "load_in_8bit": False},
    )


def get_embed_model(model_name: str = None, device: str = None):
    if not model_name:
        model_name = "BAAI/bge-small-en-v1.5"
    if not device:
        device = "cuda" if torch.cuda.is_available() else "cpu"

    return HuggingFaceEmbedding(model_name=model_name, cache_folder="./models", device=device)


Settings.llm = get_llm()
Settings.embed_model = get_embed_model()
```

Com as configurações de modelo, foi criado um LLMTextCompletionProgram para receber os parametros no template do prompt.

```python
from llama_index.core.program import LLMTextCompletionProgram
from llama_index.llms.openai import OpenAI

from entities.table_info import TableInfo

llm_text_completion_program = LLMTextCompletionProgram.from_defaults(
    output_cls=TableInfo,  # output_parser=PydanticOutputParser(output_cls=TableInfo),
    prompt_template_str=prompt_template_str,
    # llm=Settings.llm Se tiver configurado o modelo localmente
    llm=OpenAI(model="gpt-3.5-turbo"),
    verbose=True,
)
```

Foi criado duas funções, uma para verificar se o dataframe ja tem informações extraidas para evitar consumo excessivo de requisicoes na API do OpenAI, caso exista é retornado as informações que estão armazenadas no diretório ```wikitablequestions_infos_dir```,  e outra para fazer as requisições das informações de cada tabela.

```python
import json
import logging
from pathlib import Path
from typing import List, Optional

import pandas as pd
from llama_index.core.program import LLMTextCompletionProgram

from entities.table_info import TableInfo

wikitablequestions_infos_dir = "./data/WikiTableQuestions_Infos"


def get_wiketable_info_by_idx(idx: int) -> Optional[str]:
    results_gen = Path(wikitablequestions_infos_dir).glob(f"{idx}_*")
    results_list = list(results_gen)
    if len(results_list) == 0:
        return
    elif len(results_list) == 1:
        path = results_list[0]
        return TableInfo.parse_file(path)
    else:
        raise ValueError(
            f"More than one file matching index: {list(results_gen)}"
        )


def extract_wikitables_infos(dataframes: List[pd.DataFrame], llm_text_completion_program: LLMTextCompletionProgram, ):

    table_names = set()
    table_infos = []
    for idx, df in enumerate(dataframes):
        table_info = get_wiketable_info_by_idx(idx)
        if table_info:
            table_infos.append(table_info)
        else:
            while True:
                df_str = df.head(10).to_csv()
                table_info = llm_text_completion_program(
                    table_str=df_str,
                    exclude_table_name_list=str(list(table_names)),
                )
                table_name = table_info.table_name
                logging.info(f"Processed table: {table_name}")
                if table_name not in table_names:
                    table_names.add(table_name)
                    break
                else:
                    logging.info(f"Table name {table_name} already exists, trying again.")
                    pass

            out_file = f"{wikitablequestions_infos_dir}/{idx}_{table_name}.json"
            json.dump(table_info.dict(), open(out_file, "w"))
        table_infos.append(table_info)

```

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

Essa informações foram utilizadas como metadados das tabelas de cada .csv salvo nas tabelas SQL, foi usado o `sqlalchemy` para orquestrar essa parte do fluxo. 

