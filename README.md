# PS2-DatabaseSync

> A tool based on the Planetside 2 API.

Get game events and sync to database.

## How to use

1. First you need a `config.json` file in config, for example:

```json
{
  "database": {
    "host": "localhost",
    "port": 3306,
    "database": "example",
    "user": "user",
    "password": "password"
  },
  "planetside2": {
    "api": "wss://push.planetside2.com/streaming?environment=ps2&service-id=s: ...",
    "subscription": "{\"service\":\"event\", ... , \"logicalAndCharactersWithWorlds\":true}"
  }
}
```

2. You will need following third-party dependencies to run the application.

```requirements.txt
setuptools==57.0.0
mysql-connector-python==8.0.28
websockets==10.1
```

3. Use the command below to start.

```shell
python -m ps2cpcdata
```
