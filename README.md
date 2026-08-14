0#### Материалы
- [Отчёт 2025](docs/source/_static/iteration_summary/2025/PersonalAI(Отчёт)(НИР)(Skoltech-Sber)(2025).pdf)
- [Презентация работ 2025](docs/source/_static/iteration_summary/2025/PersonalAI(ПриёмкаРабот)(НИР)(Skoltech-Sber)(2025).pdf)
#### Статьи
- [PersonalAI: A Systematic Comparison of Knowledge Graph Storage and Retrieval Approaches for Personalized LLM agents](docs/source/_static/iteration_summary/2024/PersonalAI(Статья)(НИР)(Skoltech-Sber)(2024).pdf)

#### Структура файловой системы:
- debug/ - Директория с ноутбуками/скриптами для отладки кода из каталога "src".
- experiments/ - Директория с реализациями проведённых экспериментов: дообучение/обучение моделей, подбор гиперпараметров модели и т.п. Каждый эксперимент в отдельной директории. Обязательно логирование в отдельном каталоге "logs" (для каждого каталога с экспериментом свой каталог с логами): пул гиперпарметров + полученные метрики.
- notebooks/ - Директория с переиспользуемыми ноутбуками: связанные с предобработкой датасетов, формированием баз данных и т.п.
- src/ - Директория с production-кодом проекта.
- tests/ - Директория с модульными/интеграционными тестами для кода из каталога "src".
- models/ - Директория с нейросетевыми моделями (используем DVC для версионирования и совместного использования)
- data/ - Директория с датасетами/базами данных (используем DVC для версионирования и совместного использования)
- docs/ - Директория с документацией проекта.

#### Структура веток:
- dev - Предназначена для реализации функционала разрабатываемой библиотеки. Для решения конкретной задачи в рамках "dev" нужно создать от неё отдельную ветку, реализовать решение и смёржить в dev и удалить ветку из репозитория. Названия данных веток имеет следующий формат: номер issue в gitlab с описание задачи (task#N).
- test - Предназначена для написания/запуска тестов по реализованному функционалу из ветки dev. На данной стадии выполняется проверка на соответствие логики программного кода заданным функциональным требованиям.
- master - Рабочая версия кода для демонстрации заказчику. ВНИМАНИЕ: в main можно только сливать изменения из ветки test. Делать комиты в ветку напрямую запрещено!
- exp - Предназначена для проведения экспериментов. Для решения конкретной задачи в рамках "exp" нужно создать от неё отдельную ветку, реализовать решение и (после review от лида) смёржить в "exp" и удалить ветку из репозитория. Для проведения эксперимента необходимо создать отдельную директорию в каталоге "experiments"; название директории должно быть в следующем формате: "суть_эксперимента (#N)". Эксперименты могут быть вложенными: есть директория с общим названием эксперимента, в рамках которого прооводится несколько атомарных исследований.
- task#N - Предназначеная для решения конкретной/атомарной задачи, проведения эксперимента, описанной в соответствующем issue на gitlab.

##### Рабочие скрипты:
* [Построение графа](notebooks/kg_building)
* [Оценка эффективности конфигурации QA-пайплайна с использование построенного графа](experiments/qa)

##### Полезные материалы
* [MLOps](docs/source/_static/useful_material/MLOps/)
* [Организация научных исследований](docs/source/_static/useful_material/ОрганизацияНаучныхИсследований/)

##### Команды для генерации документации:
* find . -type d -name __pycache__ -exec rm -r {} \+
* sphinx-apidoc -o ../docs/tmp/ .
* make html
* make latexpdf
* make singlehtml
* make clean

##### Генерация диаграммы классов
* pyreverse -o puml -f ALL src/

##### Команды для тестироваания
* pytest --cov=src --cov-report=html ...
* pygount src/ --suffix=py --format=summary

##### Команды для проверки стиля кодовой базы
* autopep8 src # formatter
* pylint src # linter
* flake8 src # linter
* mypy src # linter

pre-commit:
* https://pre-commit.com/#pre-commit-configyaml---repos
* https://www.laac.dev/blog/automating-convention-linting-formatting-python/

dvc tutorial:
* get-start - https://dvc.org/doc/start
* remote ssh-storage - https://dvc.org/doc/user-guide/data-management/remote-storage/ssh
* remote gdrive-storage - https://dvc.org/doc/user-guide/data-management/remote-storage/google-drive

pytest tutorial:
* https://realpython.com/pytest-python-testing/#parametrization-combining-tests

archive experiments:
* tar -czvf  deepseek_231025_v2prompts.tar.gz --exclude="configs" --exclude="judge_packs" --exclude="metric_packs" --exclude="tmp_answer_packs" --exclude="tmp_judges_packs" --exclude="inference_log.txt"  deepseek_231025_v2prompts/

--------------------------------

Тех. поддержка: [Telegram](https://t.me/mmenscshikov), <m.menschikov@skoltech.ru>
