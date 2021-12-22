
if [ -f secrets.sh ]; then
  echo "Secrets already exist"
else
  password=`cat /dev/urandom | head -c 32 | base64 | head -c 32`
  echo "export SECRET_KEY=$password" > secrets.sh
fi

exit 0