FROM sentry:9.1.1

ARG SENTRY_PLUGINS="sentry-ldap-auth"
ARG SENTRY_PLUGINS_BUILDDEPS="libldap2-dev libsasl2-dev"
ARG SUPERCRONIC_URL="https://github.com/aptible/supercronic/releases/download/v0.1.8/supercronic-linux-amd64"
ARG DEBIAN_FRONTEND="noninteractive"
ARG C_ALL="C.UTF-8"

COPY root/ /

RUN set -eux; \
    \
    # Install packages
    \
    apt-get -qq update; \
    apt-get --yes --no-install-recommends install \
      busybox-static \
      curl \
      ${SENTRY_PLUGINS_BUILDDEPS}; \
    \
    # Install sentry plugins
    \
    pip install --no-cache-dir ${SENTRY_PLUGINS}; \
    \
    # Install supercronic
    \
    curl -fsSL ${SUPERCRONIC_URL} -o /usr/local/bin/supercronic && \
    chmod 0755 /usr/local/bin/supercronic; \
    \
    # Cleanup
    \
    apt-get --yes purge ${SENTRY_PLUGINS_BUILDDEPS}; \
    apt-get --yes --purge autoremove; \
    apt-get --yes clean; \
    find /tmp /var/tmp /var/lib/apt/lists /var/log/apt -mindepth 1 -delete; \
    find /var/log -type f -exec truncate -s 0 {} +
