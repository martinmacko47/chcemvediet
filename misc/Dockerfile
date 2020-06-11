FROM ubuntu:18.04

RUN \
  apt-get update && \
  apt-get install -y \
    # Base system
    gcc \
    g++ \
    gettext \
    libssl-dev \
    cron \
    git \
    # Dependencies
    apache2 \
    mysql-server \
    python \
    python-virtualenv \
    python-dev \
    libmysqlclient-dev \
    libapache2-mod-wsgi \
    libreoffice \
    imagemagick \
    libmagic1 \
    webp \
    && \
  :

# Setup user
RUN \
  addgroup --gid 1001 chcemvediet && \
  adduser --uid 1001 --gid 1001 --gecos '' --disabled-password chcemvediet && \
  :

# Setup cron
RUN \
  echo "* * * * * chcemvediet cd /home/chcemvediet/chcemvediet && env/bin/python manage.py runcrons" > /etc/cron.d/chcemvediet && \
  :

# Setup mysql
RUN \
  /etc/init.d/mysql start && \
  printf "%s\n" \
    "create database chcemvediet;" \
    "alter database chcemvediet character set utf8 collate utf8_general_ci;" \
    "grant all privileges on chcemvediet.* to chcemvediet@localhost identified by 'nbusr123';" \
    | mysql && \
  :

# Setup apache
RUN \
  a2enmod ssl && \
  openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout /root/chcemvediet.key -out /root/chcemvediet.crt -subj '/' && \
  printf "%s\n" \
    "<VirtualHost *:80>" \
    "  ServerName chcemvediet.local" \
    "  ServerAlias www.chcemvediet.local" \
    "  Redirect permanent / https://www.chcemvediet.local/" \
    "</VirtualHost>" \
    "" \
    "<VirtualHost *:443>" \
    "  ServerName chcemvediet.local" \
    "  ServerAlias www.chcemvediet.local" \
    "" \
    "  SSLEngine on" \
    "  SSLCertificateFile /root/chcemvediet.crt" \
    "  SSLCertificateKeyFile /root/chcemvediet.key" \
    "" \
    "  Alias /robots.txt /home/chcemvediet/chcemvediet/static/robots.txt" \
    "  Alias /favicon.ico /home/chcemvediet/chcemvediet/static/favicon.ico" \
    "  Alias /static/ /home/chcemvediet/chcemvediet/static/" \
    "  <Directory /home/chcemvediet/chcemvediet/static>" \
    "    Require all granted" \
    "    Options -Indexes" \
    "  </Directory>" \
    "" \
    "  WSGIScriptAlias / /home/chcemvediet/chcemvediet/chcemvediet/wsgi.py" \
    "  WSGIDaemonProcess chcemvediet user=chcemvediet group=chcemvediet python-path=/home/chcemvediet/chcemvediet:/home/chcemvediet/chcemvediet/env/lib/python2.7/site-packages" \
    "  WSGIProcessGroup chcemvediet" \
    "  <Directory /home/chcemvediet/chcemvediet/chcemvediet>" \
    "    <Files wsgi.py>" \
    "      Require all granted" \
    "    </Files>" \
    "  </Directory>" \
    "</VirtualHost>" \
    > /etc/apache2/sites-available/001-chcemvediet.conf && \
  ln -s ../sites-available/001-chcemvediet.conf /etc/apache2/sites-enabled/001-chcemvediet.conf && \
  :

# Setup imagemagick
RUN \
  sed -i 's~<policy domain="coder" rights="none" pattern="PDF" />~<policy domain="coder" rights="read|write" pattern="PDF" />~' /etc/ImageMagick-6/policy.xml && \
  :

# Clone repo
RUN \
  cd /home/chcemvediet && \
  su chcemvediet -c "git clone https://github.com/martinmacko47/chcemvediet.git" && \
  :

# Run setup
RUN \
  /etc/init.d/mysql start && \
  cd /home/chcemvediet/chcemvediet && \
  printf "%s\n" \
    # Server mode: Production mode with no email infrastructure.
    "6" \
    # Mock libreoffice?
    "n" \
    # Mock imagemagic?
    "n" \
    # Mock abbyyocr11?
    "y" \
    # Install requirements for unittesting?
    "n" \
    # Server domain
    "www.chcemvediet.local" \
    # Admin e-mail (default)
    "" \
    # Support e-mail (default)
    "" \
    # Inforequest unique e-mail (default)
    "" \
    # Default from e-mail (default)
    "" \
    # Database name
    "chcemvediet" \
    # Database user name
    "chcemvediet" \
    # Database user password
    "nbusr123" \
    # Unique cache key prefix (default)
    "" \
    # Google Custom Search API key (default)
    "" \
    # Load datasheets / Neighbourhood dummy was omitted / Delete it?
    "y" \
    # Load datasheets / Municipality dummy was omitted / Delete it?
    "y" \
    # Load datasheets / District dummy was omitted / Delete it?
    "y" \
    # Load datasheets / Region dummy was omitted / Delete it?
    "y" \
    # Admin password
    "nbusr123" \
    # Facebook OAuth Client ID (default)
    "" \
    # Facebook OAuth Secret (default)
    "" \
    # Google OAuth Client ID (default)
    "" \
    # Google OAuth Secret (default)
    "" \
    | su chcemvediet -c "PYTHONUNBUFFERED=1 python setup.py" && \
  su chcemvediet -c "env/bin/python manage.py collectstatic --noinput" && \
  :

EXPOSE 80 443
CMD \
  /etc/init.d/mysql start && \
  /etc/init.d/apache2 start && \
  /etc/init.d/cron start && \
  bash
