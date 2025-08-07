[![Validate with hassfest](https://github.com/bieniu/ha-meteo-imgw-pib/actions/workflows/hassfest.yml/badge.svg)](https://github.com/bieniu/ha-meteo-imgw-pib/actions/workflows/hassfest.yml)
[![GitHub Release][releases-shield]][releases]
[![GitHub All Releases][downloads-total-shield]][releases]
[![Buy me a coffee][buy-me-a-coffee-shield]][buy-me-a-coffee]
[![PayPal_Me][paypal-me-shield]][paypal-me]
[![Revolut.Me][revolut-me-shield]][revolut-me]


# Meteo IMGW-PIB

Meteo IMGW-PIB custom integration uses data from the IMGW-PIB API (Poland only) to present weather condition in Home Assistant.

![obraz](https://github.com/user-attachments/assets/c870f780-7cb2-4eab-b5e0-9783c1c7b79f)

## Installation

You can install this integration manually or via [HACS](https://hacs.xyz) if you add the repository to the custom repository list (**three dot menu** >> **Custom repositories**)

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=bieniu&repository=https%3A%2F%2Fgithub.com%2Fbieniu%2Fha-meteo-imgw-pib&category=integration)

## Configuration

To configure integration in Home Assistant, go to **Settings** >> **Devices & services** >> **Add integration** >> **Meteo IMGW-PIB** or use My Home Assistant link.

[![Open your Home Assistant instance and start setting up a new integration.](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=meteo_imgw_pib)

## How to debug

To debug the integration add this to your `logger` configuration:

```yaml
# configuration.yaml file
logger:
  default: warning
  logs:
    custom_components.meteo_imgw_pib: debug
    imgw_pib: debug
```

[releases]: https://github.com/bieniu/ha-meteo-imgw-pib/releases
[releases-shield]: https://img.shields.io/github/release/bieniu/ha-meteo-imgw-pib.svg?style=popout
[downloads-total-shield]: https://img.shields.io/github/downloads/bieniu/ha-meteo-imgw-pib/total
[buy-me-a-coffee-shield]: https://img.shields.io/static/v1.svg?label=%20&message=Buy%20me%20a%20coffee&color=6f4e37&logo=buy%20me%20a%20coffee&logoColor=white
[buy-me-a-coffee]: https://www.buymeacoffee.com/QnLdxeaqO
[paypal-me-shield]: https://img.shields.io/static/v1.svg?label=%20&message=PayPal.Me&logo=paypal
[paypal-me]: https://www.paypal.me/bieniu79
[revolut-me]: https://revolut.me/maciejbieniek
[revolut-me-shield]: https://img.shields.io/static/v1.svg?label=%20&message=Revolut&logo=revolut
