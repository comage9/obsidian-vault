# Canon G2000/G2010/G2910 Printer Setup — Blog Reference

Source: https://eventhorizon.tistory.com/152 ("ubuntu 20.04/21.04 Canon G2910 Driver 설치")

## Main Method (PPA)

```bash
sudo add-apt-repository ppa:thierry-f/fork-michael-gruz
sudo apt update
sudo apt install cnijfilter2 scangearmp2
sudo apt install printer-driver-gutenprint system-config-printer
```

Procedure:
1. Connect USB cable
2. Driver auto-detection
3. Select "Canon" (recommended vendor)
4. Select "Canon G2000" printer model
5. Print test page

## Fallback Method (Direct Download)

For Ubuntu 21.04+ where cnijfilter2 PPA package may fail:

```bash
wget http://gdlp01.c-wss.com/gds/5/0100006265/01/cnijfilter2-5.00-1-deb.tar.gz
tar xvzf cnijfilter2-5.00-1-deb.tar.gz
cd cnijfilter2-5.00-1-deb
./install.sh
```

## Notes

- The blog title says "G2910" but the installation selects **Canon G2000** — the G2000 series driver is backward-compatible with G2010, G2900, and G2910 models.
- Gutenprint already has `gutenprint.5.3://bjc-G2000-series/expert` pre-installed on modern Ubuntu systems (no PPA needed for Gutenprint).
- PPA `ppa:thierry-f/fork-michael-gruz` provides the proprietary Canon `cnijfilter2` driver for better quality.
- System: Ubuntu 20.04/21.04, but the approach works on Ubuntu 22.04/24.04+ as well.
