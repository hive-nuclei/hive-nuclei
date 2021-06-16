hive-nuclei
===================

![logo](https://hive-nuclei.github.io/images/logo.jpeg) 

[![Site][site-label]][site-link]
[![Required OS][os-label]][os-link]
[![Python3 version][python3-versions-label]][python3-versions-link]
[![License][license-label]][license-link]
[![Version][version-label]][version-link]

[site-label]: https://hive-nuclei.github.io/images/labels/site.svg
[site-link]: https://hive-nuclei.github.io/
[os-label]: https://hive-nuclei.github.io/images/labels/os.svg
[os-link]: https://en.wikipedia.org/wiki/Operating_system
[python3-versions-label]: https://hive-nuclei.github.io/images/labels/python3.svg
[python3-versions-link]: https://www.python.org/downloads/release/python-360/
[license-label]: https://hive-nuclei.github.io/images/labels/license.svg
[license-link]: https://github.com/hive-nuclei/hive-nuclei/blob/main/LICENSE
[version-label]: https://hive-nuclei.github.io/images/labels/version.svg
[version-link]: https://github.com/hive-nuclei/hive-nuclei/releases

## Description

hive-nuclei is a python library for parsing nuclei output and send it to Hive.

[![demo video](https://hive-nuclei.github.io/images/demo.gif)](https://youtu.be/TJb65O_pe2c)

hive-nuclei easy to use:

```shell
$ cat ~/.hive/config.yaml
password: strong_password
project_id: 2b10f974-3215-4a4e-9fb7-04be8ac5202e
proxy: http://127.0.0.1:8081
server: https://hive.corp.test.com
username: user@mail.con
$ nuclei -t technologies/ -target http://server.ispa.cnr.it/ | hive-nuclei

                       __     _
     ____  __  _______/ /__  (_)
    / __ \/ / / / ___/ / _ \/ /
   / / / / /_/ / /__/ /  __/ /
  /_/ /_/\__,_/\___/_/\___/_/   v2.3.7

		projectdiscovery.io

[INF] Loading templates...
[INF] [landrayoa-detect] LandrayOA detect (@YanYun) [info]
....
[INF] [artica-web-proxy-detect] Artica Web Proxy Detect (@dwisiswant0) [info]
[INF] Loading workflows...
[INF] Reduced 228 requests to 188 (44 templates clustered)
[INF] Using 104 rules (104 templates, 0 workflows)
[2021-06-10 15:42:56] [apache-version-detect] [http] [info] http://server.ispa.cnr.it/ [Apache/2.4.7 (Ubuntu)]
[2021-06-10 15:42:56] [default-apache2-ubuntu-page] [http] [info] http://server.ispa.cnr.it/
[2021-06-10 15:42:56] [tech-detect:apache] [http] [info] http://server.ispa.cnr.it/

[INF] [hive-nuclei] Making Hive record: [info] apache-version-detect: http://server.ispa.cnr.it/ for host: 150.145.88.94:80 (@_generic_human_) [info]
[INF] [hive-nuclei] Making Hive record: [info] default-apache2-ubuntu-page: http://server.ispa.cnr.it/ for host: 150.145.88.94:80 (@_generic_human_) [info]
[INF] [hive-nuclei] Making Hive record: [info] tech-detect:apache: http://server.ispa.cnr.it/ for host: 150.145.88.94:80 (@_generic_human_) [info]
```

You can parse nuclei json output:

```shell
$ nuclei -t technologies/ -target http://server.ispa.cnr.it/ -json | hive-nuclei -j

                       __     _
     ____  __  _______/ /__  (_)
    / __ \/ / / / ___/ / _ \/ /
   / / / / /_/ / /__/ /  __/ /
  /_/ /_/\__,_/\___/_/\___/_/   v2.3.7

		projectdiscovery.io

[INF] Loading templates...
[INF] [landrayoa-detect] LandrayOA detect (@YanYun) [info]
....
[INF] [artica-web-proxy-detect] Artica Web Proxy Detect (@dwisiswant0) [info]
[INF] Loading workflows...
[INF] Reduced 228 requests to 188 (44 templates clustered)
[INF] Using 104 rules (104 templates, 0 workflows)
{"templateID":"default-apache2-ubuntu-page","info":{"severity":"info","tags":"tech,apache","reference":"https://www.shodan.io/search?query=http.title%3A%22Apache2+Ubuntu+Default+Page%22","name":"Apache2 Ubuntu Default Page","author":"dhiyaneshDk"},"type":"http","host":"http://server.ispa.cnr.it/","matched":"http://server.ispa.cnr.it/","ip":"150.145.88.94","timestamp":"2021-06-10T15:44:19.630982+03:00"}
{"templateID":"apache-version-detect","info":{"severity":"info","name":"Apache Version","author":"philippedelteil","description":"Some Apache servers have the version on the response header. The OpenSSL version can be also obtained"},"type":"http","host":"http://server.ispa.cnr.it/","matched":"http://server.ispa.cnr.it/","extracted_results":["Apache/2.4.7 (Ubuntu)"],"ip":"150.145.88.94","timestamp":"2021-06-10T15:44:19.631455+03:00"}
{"templateID":"tech-detect","info":{"severity":"info","tags":"tech","name":"Wappalyzer Technology Detection","author":"hakluke"},"matcher_name":"apache","type":"http","host":"http://server.ispa.cnr.it/","matched":"http://server.ispa.cnr.it/","ip":"150.145.88.94","timestamp":"2021-06-10T15:44:19.827086+03:00"}

[INF] [hive-nuclei] Making Hive record: [info] Apache2 Ubuntu Default Page (default-apache2-ubuntu-page): http://server.ispa.cnr.it/ for host: 150.145.88.94:80 (@_generic_human_) [info]
[INF] [hive-nuclei] Making Hive record: [info] Apache Version (apache-version-detect): http://server.ispa.cnr.it/ for host: 150.145.88.94:80 (@_generic_human_) [info]
[INF] [hive-nuclei] Making Hive record: [info] Wappalyzer Technology Detection (tech-detect): http://server.ispa.cnr.it/ for host: 150.145.88.94:80 (@_generic_human_) [info]
```

You can parse nuclei output file

```shell
$ nuclei -t technologies/ -target http://server.ispa.cnr.it/ -json > /tmp/nuclei.json
$ hive-nuclei -jf /tmp/nuclei.json
{"templateID":"apache-version-detect","info":{"name":"Apache Version","author":"philippedelteil","description":"Some Apache servers have the version on the response header. The OpenSSL version can be also obtained","severity":"info"},"type":"http","host":"http://server.ispa.cnr.it/","matched":"http://server.ispa.cnr.it/","extracted_results":["Apache/2.4.7 (Ubuntu)"],"ip":"150.145.88.94","timestamp":"2021-06-10T15:57:27.791883+03:00"}
{"templateID":"default-apache2-ubuntu-page","info":{"name":"Apache2 Ubuntu Default Page","author":"dhiyaneshDk","severity":"info","tags":"tech,apache","reference":"https://www.shodan.io/search?query=http.title%3A%22Apache2+Ubuntu+Default+Page%22"},"type":"http","host":"http://server.ispa.cnr.it/","matched":"http://server.ispa.cnr.it/","ip":"150.145.88.94","timestamp":"2021-06-10T15:57:27.794234+03:00"}
{"templateID":"tech-detect","info":{"name":"Wappalyzer Technology Detection","author":"hakluke","severity":"info","tags":"tech"},"matcher_name":"apache","type":"http","host":"http://server.ispa.cnr.it/","matched":"http://server.ispa.cnr.it/","ip":"150.145.88.94","timestamp":"2021-06-10T15:57:27.807338+03:00"}

[INF] [hive-nuclei] Making Hive record: [info] Apache Version (apache-version-detect): http://server.ispa.cnr.it/ for host: 150.145.88.94:80 (@_generic_human_) [info]
[INF] [hive-nuclei] Making Hive record: [info] Apache2 Ubuntu Default Page (default-apache2-ubuntu-page): http://server.ispa.cnr.it/ for host: 150.145.88.94:80 (@_generic_human_) [info]
[INF] [hive-nuclei] Making Hive record: [info] Wappalyzer Technology Detection (tech-detect): http://server.ispa.cnr.it/ for host: 150.145.88.94:80 (@_generic_human_) [info]
```

## Python versions

 - Python 3.6
 - Python 3.7
 - Python 3.8
 - Python 3.9

## Dependencies

 - [marshmallow](https://pypi.org/project/marshmallow/)
 - [colorama](https://pypi.org/project/colorama/)  
 - [hive-library](https://pypi.org/project/hive-library/)

## Installing

hive-nuclei can be installed with [pip](https://pypi.org/project/hive-nuclei/):
```shell
pip3 install hive-nuclei
```

Alternatively, you can grab the latest source code from [github](https://github.com/hive-nuclei/hive-nuclei.git):
```shell
git clone https://github.com/hive-nuclei/hive-nuclei.git
cd hive-nuclei
python3 setup.py install
```
