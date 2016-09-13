# Media Player Components

- place the file in the "custom_components\media_player directory" under your ".homeassistant" home directory or "config" directory

## Anthem MRX

- Tested with the Anthem MRX500 with a Global Cache iTach Serial to IP adapter.
- MRXx10 and MRXx20 models will not work with this but it could be
    modified to work with those models. I do not have a test receiver to develop it but
    if you do get in touch with me on the Home Assistant forum and we might be able to
    develop this code to support them.


### Example config
```yaml
media_player:
- platform: anthem_mrx
  name: anthem_zone1
  host: 192.168.2.200
  port: 4999
  mrxzone: 1
  minvol: -60
  maxvol: -30

- platform: anthem_mrx
  name: anthem_zone2
  host: 192.168.2.200
  port: 4999
  mrxzone: 2
  minvol: -45
  maxvol: -25
```
