sudo adduser superanton
groups superanton
sudo usermod -aG sudo superanton
$ su - superanton

uvicorn main:app --reload