# Press Release Analyzer

Бекенд для приложения: создание данных, обработка, процессинг и генерация файлов

Код написан с использованием лучших подходов на Django, с использованием Celery. Так же есть CI/CD, тесты, Docker

## Basic Commands

### Runserver

    $ ./manage.py migrate
    $ ./manage.py runserver_plus

### Type checks

Running type checks with mypy:

    $ mypy press_release_nl

#### Running tests with pytest

    $ pytest

### Setting Up Your Users

-   To create a **superuser account**, use this command:

        $ python manage.py createsuperuser

### Celery

This app comes with Celery.

To run a celery worker:

``` bash
cd press_release_nl
celery -A config.celery_app worker -l info
```

made with [cookiecutter-django](https://github.com/Alexander-D-Karpov/cookiecutter-django)
