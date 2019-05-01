@test 'Docker image test:' { :; }

@test '  sentry version' {
  run sentry --version
  [ "$output" = "sentry, version 9.1.1" ]
}

@test '  sentry-ldap-auth is installed' {
  run pip show sentry-ldap-auth
  [ "$status" -eq 0 ]
}

@test '  curl is installed' {
  run command -v curl
  [ "$status" -eq 0 ]
}

@test '  supercronic is installed' {
  run command -v supercronic
  [ "$status" -eq 0 ]
}
