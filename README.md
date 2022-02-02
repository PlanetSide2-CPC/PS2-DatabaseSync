# PS2-DatabaseSync

![GitHub release (latest by date)](https://img.shields.io/github/v/release/PlanetSide2-CPC/PS2-DatabaseSync)
[![GitHub issues](https://img.shields.io/github/issues/PlanetSide2-CPC/PS2-DatabaseSync)](https://github.com/PlanetSide2-CPC/PS2-DatabaseSync/issues)
[![GitHub license](https://img.shields.io/github/license/PlanetSide2-CPC/PS2-DatabaseSync)](https://github.com/PlanetSide2-CPC/PS2-DatabaseSync/blob/master/LICENSE)

> A tool based on the Planetside 2 API.

Get game events and sync to database.

## Documentation

If you just want to run the program, then the [quickstart](README.md#Quickstart) guide is all you need.

See https://github.com/PlanetSide2-CPC/PS2-DatabaseSync/pull/3 for how to add a new handler.

## Features

- Support custom subscription events.
- Only use async sync, no threading.

## Quickstart

This guide is only meant to cover the most basic usage of the library.

### Installation

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

Or it can be installed automatically using setup.py .

```shell
python -m pip install .
```

### Run the program

Use the command below to start.

```shell
python -m ps2cpcdata
```

## Contributing

Issues Tracker: https://github.com/PlanetSide2-CPC/PS2-DatabaseSync/issues
