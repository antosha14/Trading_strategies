conda env list
conda create -n web-Fast-Api
conda activate web-Fast-Api
conda list -n web-Fast-Api

conda env config vars list
conda env config vars set secret_password=value
conda env config vars unset my_var -n test-env #Конфиг среды с конкретным именем
