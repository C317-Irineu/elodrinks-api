# EloDrinks API

**Serviço de API para o projeto EloDrinks da matéria C317**

## Descrição
Esta é uma API desenvolvida em **FastAPI** que recebe informações sobre o orçamento, realiza os calculos necessários e controla os processos de pagamento.

## Tecnologias Utilizadas
- **FastAPI** - Framework para desenvolvimento de APIs em Python
- **MongoDB** - Banco de dados orientado a documentos
- **Docker** - Para conteinerização da aplicação

  ![python](https://img.shields.io/badge/Python-100C10?style=for-the-badge&logo=Python&logoColor=pink)
  ![FastAPI](https://img.shields.io/badge/FastAPI-100C10?style=for-the-badge&logo=FastAPI&logoColor=ciano)
  ![MongoDB](https://img.shields.io/badge/MongoDB-100C10?style=for-the-badge&logo=MongoDB&logoColor=green)
  ![Docker](https://img.shields.io/badge/Docker-100C10?style=for-the-badge&logo=Docker&logoColor=Blue)

## Estrutura do Mongo

```sh
{
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["name", "email", "phone", "budget"],
        "properties": {
            "name": {
                "bsonType": "string",
                "description": "Nome do cliente, obrigatório"
            },
            "email": {
                "bsonType": "string",
                "pattern": "^.+@.+\\..+$",
                "description": "Email do cliente, obrigatório"
            },
            "phone": {
                "bsonType": "string",
                "description": "Telefone do cliente, obrigatório"
            },
            "budget": {
                "bsonType": "object",
                "required": ["descricao", "type", "date", "num_barmans", "num_guests", "time", "package"],
                "properties": {
                    "descricao": {
                        "bsonType": "string",
                        "description": "Descrição do orçamento, obrigatório"
                    },
                    "type": {
                        "bsonType": "string",
                        "description": "Tipo de evento, obrigatório"
                    },
                    "date": {
                        "bsonType": "date",
                        "description": "Data do orçamento, obrigatório"
                    },
                    "num_barmans": {
                        "bsonType": "int",
                        "description": "Numero de barmans, obrigatório"
                    },
                    "num_guests": {
                        "bsonType": "int",
                        "description": "Numero de convidados, obrigatório"
                    },
                    "time": {
                        "bsonType": "double",
                        "description": "Quantidade de horas de festa, obrigatório"
                    },
                    "package": {
                        "bsonType": "string",
                        "description": "Pacote escolhido, obrigatório"
                    },
                    "extras": {
                        "bsonType": "list",
                        "description": "Lista com valores adicionais"
                    }
                }
            }
        }
    }
}
```

## Instalação e Execução

### 1. Clonar o repositório
```sh
 git clone https://github.com/C317-Irineu/elodrinks-api.git
 cd elodrinks-api
```

### 2. Construir e executar o container Docker
```sh
docker build -t user/elodrinks-api:1.0 .
docker run -p 8000:8000 user/elodrinks-api:1.0
```

### 3. Acessar a API
Acesse a documentação interativa no navegador:
```
http://localhost:8000/docs
```

## Licença
Este projeto está sob a licença.
