# Home Assistant - Dyson Pure Cool Link Fan using local polling

## Configuration

```yaml
dyson_fan:
  name: "Dyson Living Room"
  password: "xxxxxxxx"
  serial: "XXX-XX-XXXXXXXX"
  ip_address: "XXX.XXX.XXX.XXX"
  type: XXX
```

```password``` is the "Product Wi-Fi Password" listed on your Dyson

```serial``` is part of the "Product SSID" listed on your Dyson. Eg.: DYSON-NH8-US-JGQ1245A-475 => the serial number is between ```DYSON``` and ```475``` => ```NH8-US-JGQ1245A```

```type``` is part of the "Product SSID" listed on your Dyson. Eg.: DYSON-NH8-US-JGQ1245A-475 => the type is the last digits after the dash => ```475```

```ip_address``` is the IP of the Dyson on your local network

