if $TRAVIS_SECURE_ENV_VARS; then
  python pywikibot/pwb.py -dir:. -pass:$COPTR_PW login
else
  echo "No secure variables available - cannot login!"
  exit 1;
fi
