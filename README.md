# Обозреватель цепочки блоков

## Описание
Домашняя работа, 
посвященная изучению микросервисной архитектуры, 
выполняемая в рамках курса«Архитектор программного обеспечения»

## Постановка задачи

### Общая
Разработать сервис, позволяющий пользователю отслеживать баланс своего кошелька, 
представленный как разница полученых доходов и списанных расходов для принадлежащих пользователю адресов 

### В рамках первой части домащней работы
Разработать сервис, имеющий следующие возможности:
* регистрация пользователя
* аутентификация пользователя
* создание кошелька пользователя
* получение списка кошельков пользователя

## Ограничения
Данный проект, являясь учебным, содержит некоторые ограничения:
* отслеживания адреса произодится только с момента его регистрации

## Архитетура проекта


![](architecture.svg)

В данный момент реализован наивный вариант аутентификации - 
электронный адрес пользователя после прямой сверки паролей открыто сохраняется в cookie.

Сервисы отмеченные пунктиром будут реализованы позднее.

Backend отвечает за формирование ответов на запросы.

Loader отвечает за выгрузку блоков из корневых узлов цепочки блоков (blockchain)

## Описание контрактов

***backend***

https://app.swaggerhub.com/apis/mas-login/blockchain-explorer/1.0.1

## Запуск сервиса
```
    docker-compose up explorer
```

## Выполнение ручной проверки

установка http клиента (нет никаких препятствий для использования cUrl)
```
    apt-get install httpie
```

создание и получения кошелька
```
    http --session=explorer -v http://127.0.0.1:18000/signup email=user@site.net password=12345678

    http --session=explorer -v http://127.0.0.1:18000/signin email=user@site.net password=12345678

    http --session=explorer -v http://127.0.0.1:18000/wallets address=1234567890ABCDEF

    http --session=explorer -v http://127.0.0.1:18000/wallets 

```


## Запуск самопроверки
```
    docker-compose run explorer-test
```
