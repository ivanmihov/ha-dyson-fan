# Home Assistant - Dyson Pure Cool Link Fan using local polling

## Installation (HACS) - Highly Recommended
1. Have [HACS](https://github.com/custom-components/hacs) installed, this will allow you to easily update
2. Add `https://github.com/ivanmihov/ha-dyson-fan` as a [custom repository](https://custom-components.github.io/hacs/usage/settings/#add-custom-repositories) as Type: Integration
3. Click install under "Dyson Fan", restart your instance.

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