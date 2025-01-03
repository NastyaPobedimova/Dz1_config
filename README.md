# **Задание №1**
Разработать эмулятор для языка оболочки ОС. Необходимо сделать работу
эмулятора как можно более похожей на сеанс shell в UNIX-подобной ОС.
Эмулятор должен запускаться из реальной командной строки, а файл с
виртуальной файловой системой не нужно распаковывать у пользователя.
Эмулятор принимает образ виртуальной файловой системы в виде файла формата
zip. Эмулятор должен работать в режиме CLI.

Конфигурационный файл имеет формат toml и содержит:

- Имя пользователя для показа в приглашении к вводу.
- Путь к архиву виртуальной файловой системы.
- Необходимо поддержать в эмуляторе команды ls, cd и exit, а также следующие команды:

1.uname.

2.history.

3.mv.

Все функции эмулятора должны быть покрыты тестами, а для каждой из поддерживаемых команд необходимо написать 3 теста.

# Установка
Перед началом работы с программой требуется скачать репозиторий и необходимую библиотеку для тестов. Для этого можно воспользоваться командами ниже.
```Bash
git clone https://github.com/NastyaPobedimova/Dz1_config
```
```Bash
pip install -U pytest
```
# Запуск

Перед запуском необходимо клонировать репозиторий в среду разработки.

Обязательно прописать путь к файловой системе в config.toml.

Переход в директорию Dz1_config:
```Bash
cd Dz1_config
```
Запуск main.py:
```Bash
py main.py config.toml
```
Запуск тестов
```Bash
pytest test.py -v
```

# Команды

``` ls <path> ``` - Список файлов и директорий

``` cd <path> ``` - Смена директории

``` exit ``` - Выход из эмулятора

``` uname ``` - Вывод информации о системе

``` history ``` - Вывод истории ввода

``` mv <file_path> <folder_path> ``` - Перемещение файлов из одного места в другое

# Тесты

## ls
![](https://github.com/NastyaPobedimova/Dz1_config/blob/main/Test/ls.png)

## cd
![](https://github.com/NastyaPobedimova/Dz1_config/blob/main/Test/cd.png)

## exit
![](https://github.com/NastyaPobedimova/Dz1_config/blob/main/Test/exit.png)

## uname
![](https://github.com/NastyaPobedimova/Dz1_config/blob/main/Test/uname.png)

## history
![](https://github.com/NastyaPobedimova/Dz1_config/blob/main/Test/history.png)

## mv
![](https://github.com/NastyaPobedimova/Dz1_config/blob/main/Test/mv.png)

## Общие тесты через pytest
![](https://github.com/NastyaPobedimova/Dz1_config/blob/main/Test/%D0%A2%D0%B5%D1%81%D1%82%D1%8B.png)
