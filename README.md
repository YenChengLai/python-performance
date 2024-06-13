# python-performance

This project containing performance issues I encountered in projects.

## Build up the environment

1. Go to the project folder in command line and run the below command:

    ```.sh
    source ./init.sh
    ```

## Project Directory

``` text
/python-performance
├── .cmds
│   ├── requirements.txt
│   └── setup.sh
├── cases
│   └── mac_device_mapping
│       ├── device_clients.json
│       ├── keep_clients.json
│       └── performance.py
├── init.sh
└── README.md
```

## Using Py-spy

In the root directory, run the below command:

```.ssh
py-spy top -- python cases/mac_device_mapping/performance.py
```

You can also run the below command while py-spy is running. It'll show the detailed line number.

```.ssh
? l
```
