@test 'Docker image test:' { :; }

@test '  sentry version' {
  run sentry --version
  [ "$output" = "sentry, version $SENTRY_VERSION" ]
}

@test '  sentry-ldap-auth is installed' {
  pip show sentry-ldap-auth
}

@test '  curl is installed' {
  command -v curl
}

@test '  supercronic is installed' {
  command -v supercronic
}
