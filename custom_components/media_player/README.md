# Media Player Components

- place the file in the "custom_components\media_player directory" under your ".homeassistant" home directory or "config" directory

## Anthem MRX

- Tested with the Anthem MRX500 with a Global Cache iTach Serial to IP adapter.


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

