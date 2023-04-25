# RPi EvilTwin Portable Access Point (Version 2)
This is built upon https://github.com/NickJongens/PiEvilTwin.

## Disclaimer
I AM NOT responsivle for any damages caused by the misuse of this tool. Performing attacks on the public is illegal and requires permission from everyone on / around the network that will be effected.

# Set up
```
./install.sh
```

# Usage
## Run the original tool
Start
```bash
./PiEvilTwinStart.sh
```

Stop
```bash
./stop.sh
```

You can also run `./start-on-boot.sh` to make it auto start on boot.

## Run new cli version
```
python3 main-cli.py
```

This will error and exit if you do not have an external wifi extender. (I will fix this later.)

## GUI version
```
python3 main.py
```

Bit behind the cli version but works well enough.

# To Do
Working on the cli verison currently, GUI will be updated once cli is perfect.

Create a db for scanned AP's

Finish the tool.