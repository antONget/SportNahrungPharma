# preprocessing
## подготовка списка зависимостей
```bash
pip freeze > requirements.txt
```

# Разворачивание Bot на сервере
## Разархивируйте проект в выбранную вами папку на сервере или склонируйте репозитарий из github выполнив команду
```bash
git clone https://github.com/antONget/prosoft.git
```
## Для разворачивания телеграм-бота последовательно выполните команды:
### Создайте виртуальное окружения для проекта
```bash
python -m venv venv
```
### Активируйте его
### Windows:
```bash
venv\Scripts\activate.bat
```
### Linux
```bash
venv/bin/activate
```
### Установите требуемы зависисмости для проекта
```bash 
pip install -r requirements.txt
```
### Необезательный пункт
Внесите изменения в файл .env в папке config (если требуется изменить токен бота или id superadmin)
```python 
BOT_TOKEN="token_your_telegam_bot"
ADMIN_IDS="telegram_id manager(or admin), who will receive messages with orders"
```
### Запустите бота
```bash 
python3 sportnahrangpharm_bot.py 
```

### PM2
Еще один способ запустить бота — использовать менеджер процессов PM2. PM2 автоматически перезапускает бота и сохраняет логи.
Установите следующие пакеты:
```bash 
sudo apt install nodejs
sudo apt install npm
```
Далее установите PM2:
```bash 
npm install pm2 -g
```
Для запуска бота перейдите в директорию с ботом и запустите его командой:
```bash 
pm2 start sportnahrangpharm_bot.py --interpreter=python3
```



