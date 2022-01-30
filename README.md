# PS2-DatabaseSync

> A tool based on the Planetside 2 API.

Get game events and sync to database.

## How to use

1. First you need a `database.json` file in config, for example:

```json
{
  "host": "localhost",
  "port": 3306,
  "database": "example",
  "user": "my_account",
  "password": "your_password"
}
```

2. You will need following third-party dependencies to run the application.

```requirements.txt
pymysql >= 1.0.2
websockets >= 10.1
```

3. Use the command below to start.

```shell
python -m update_database.py
```
