$ sudo apt install docker-ce docker-ce-cli containerd.io
$ sudo docker run hello-world
$ docker pull postgres
$ docker run --name main_postgres -e POSTGRES_PASSWORD=mysecretpassword -d postgres
docker compose up -d в дирректории где лежит compose.yml файл   d
docker compose watch #Чтобы изменения из файлов сразу отражалить в запущенном контейнером сервере