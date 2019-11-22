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
  echo \
    "create database chcemvediet;\n" \
    "alter database chcemvediet character set utf8 collate utf8_general_ci;\n" \
    "grant all privileges on chcemvediet.* to chcemvediet@localhost identified by 'nbusr123';\n" \
    | mysql && \
  :

# Setup apache
RUN \
  a2enmod ssl && \
  openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout /root/chcemvediet.key -out /root/chcemvediet.crt -subj '/' && \
  echo \
    "<VirtualHost *:80>\n" \
    "  ServerName chcemvediet.local\n" \
    "  ServerAlias www.chcemvediet.local\n" \
    "  Redirect permanent / https://www.chcemvediet.local/\n" \
    "</VirtualHost>\n" \
    "\n" \
    "<VirtualHost *:443>\n" \
    "  ServerName chcemvediet.local\n" \
    "  ServerAlias www.chcemvediet.local\n" \
    "  \n" \
    "  SSLEngine on\n" \
    "  SSLCertificateFile /root/chcemvediet.crt\n" \
    "  SSLCertificateKeyFile /root/chcemvediet.key\n" \
    "  \n" \
    "  Alias /robots.txt /home/chcemvediet/chcemvediet/static/robots.txt\n" \
    "  Alias /favicon.ico /home/chcemvediet/chcemvediet/static/favicon.ico\n" \
    "  Alias /static/ /home/chcemvediet/chcemvediet/static/\n" \
    "  <Directory /home/chcemvediet/chcemvediet/static>\n" \
    "    Require all granted\n" \
    "    Options -Indexes\n" \
    "  </Directory>\n" \
    "  \n" \
    "  WSGIScriptAlias / /home/chcemvediet/chcemvediet/chcemvediet/wsgi.py\n" \
    "  WSGIDaemonProcess chcemvediet user=chcemvediet group=chcemvediet python-path=/home/chcemvediet/chcemvediet:/home/chcemvediet/chcemvediet/env/lib/python2.7/site-packages\n" \
    "  WSGIProcessGroup chcemvediet\n" \
    "  <Directory /home/chcemvediet/chcemvediet/chcemvediet>\n" \
    "    <Files wsgi.py>\n" \
    "      Require all granted\n" \
    "    </Files>\n" \
    "  </Directory>\n" \
    "</VirtualHost>\n" \
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
  echo \
    # Server mode: Production mode with no email infrastructure.
    "6\n" \
    # Mock libreoffice?
    "n\n" \
    # Mock imagemagic?
    "n\n" \
    # Mock abbyyocr11?
    "y\n" \
    # Install requirements for unittesting?
    "n\n" \
    # Server domain
    "www.chcemvediet.local\n" \
    # Admin e-mail (default)
    "\n" \
    # Support e-mail (default)
    "\n" \
    # Inforequest unique e-mail (default)
    "\n" \
    # Default from e-mail (default)
    "\n" \
    # Database name
    "chcemvediet\n" \
    # Database user name
    "chcemvediet\n" \
    # Database user password
    "nbusr123\n" \
    # Unique cache key prefix (default)
    "\n" \
    # Google Custom Search API key (default)
    "\n" \
    # Load datasheets / Neighbourhood dummy was omitted / Delete it?
    "y\n" \
    # Load datasheets / Municipality dummy was omitted / Delete it?
    "y\n" \
    # Load datasheets / District dummy was omitted / Delete it?
    "y\n" \
    # Load datasheets / Region dummy was omitted / Delete it?
    "y\n" \
    # Admin password
    "nbusr123\n" \
    # Facebook OAuth Client ID (default)
    "\n" \
    # Facebook OAuth Secret (default)
    "\n" \
    # Google OAuth Client ID (default)
    "\n" \
    # Google OAuth Secret (default)
    "\n" \
    # Twitter OAuth Client ID (default)
    "\n" \
    # Twitter OAuth Secret (default)
    "\n" \
    # LinkedIn OAuth Client ID (default)
    "\n" \
    # LinkedIn OAuth Secret (default)
    "\n" \
    | sed 's/^ //' \
    | su chcemvediet -c "PYTHONUNBUFFERED=1 python setup.py" && \
  su chcemvediet -c "env/bin/python manage.py collectstatic --noinput" && \
  :

EXPOSE 80 443
CMD \
  /etc/init.d/mysql start && \
  /etc/init.d/apache2 start && \
  /etc/init.d/cron start && \
  bash
