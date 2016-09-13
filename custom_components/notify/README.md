# Notify Components

- Place the file in the "custom_components\notify directory" under your ".homeassistant" home directory or "config" directory

## IP2SL

- This is not really a notify component but I used notify as the base platform
 as it provided an easy integration into HA.
- It allows for the sending of onetime commands to an IP socket.
- In the example below and the configuration that I have is sending "sendir" commands to an Global Cache iTach IP2IR device.
- All "messages" or commands are terminated with "\r" or carriage return.
I may make this customisable later.
- I called it IP2SL as even though I am sending IR commands they are really just serial commands activating the sending of IR.
- I am currently not doing anything with the returned data apart from logging it at "info" level.
- In this usage example I have two scripts that I can call to turn my panasonic tv on or off.


### Example config
```yaml
notify:
- name: ip2sl
  platform: ip2sl
  host: 192.168.2.210
  port: 4998
  timeout: 10 # Optional
```

### Example usage in script
```yaml
script:
  tv_on:
    sequence:
      - service: notify.ip2sl
        data:
            message: "sendir,1:1,1,36764,1,1,128,63,16,16,16,48,16,16,16,16,\
                      16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,\
                      16,48,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,\
                      16,16,16,48,16,16,16,16,16,16,16,16,16,16,16,16,16,16,\
                      16,16,16,16,16,48,16,48,16,48,16,48,16,48,16,16,16,16,\
                      16,16,16,48,16,48,16,48,16,48,16,48,16,16,16,48,16,2712"

  tv_off:
    sequence:
      - service: notify.ip2sl
        data:
            message: "sendir,1:1,1,36764,1,1,128,63,16,16,16,48,16,16,16,16,\
                      16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,\
                      16,48,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,\
                      16,16,16,48,16,16,16,16,16,16,16,16,16,16,16,16,16,16,\
                      16,16,16,48,16,48,16,48,16,48,16,48,16,48,16,16,16,16,\
                      16,48,16,48,16,48,16,48,16,48,16,48,16,16,16,48,16,2712"
```
*Note: To split the long string without introducing additional spaces
double quotes are required with a backslash \ at the end of every line.*

Configuration variables:

- **host** (*Required*): The IP or hostname of the device.
- **port** (*Required*): The port of the device.
- **name** (*Optional*): Setting the optional parameter `name` allows multiple notifiers to be created. The default value is `notify`. The notifier will bind to the service `notify.NOTIFIER_NAME`.
- **timeout** (*Optional*): The socket timeout time in seconds. Defaults to 10s.
