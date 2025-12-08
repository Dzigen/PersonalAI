#### Отчётные материалы
- [НИР 2025](https://drive.google.com/file/d/1nyIQT04-U-FYk62zW8fX1YXudolp0S24/view?usp=sharing)
- [PersonalAI: A Systematic Comparison of Knowledge Graph Storage and Retrieval Approaches for Personalized LLM agents](https://drive.google.com/file/d/1wcMtug5WRyAntgb-6hQ2IWzbyd3qEK8x/view?usp=sharing)

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

Пример работы с описанной структурой веток:

![alt text](https://github.com/zer0o0ne/Personal-AI/blob/dev/docs/branch_workflow.jpg)

##### Полезные материалы (структура ML-проекта):
* https://drive.google.com/file/d/1g0tzALqKygFTtzA-C5l5ZOdC9tKiUTzc/view?usp=sharing

##### Команда для деплоя контейнеров:
* docker build -t m.menschikov/agent_api:v2 .
* docker run -d -p 45678:4567 -v ./models:/app/models -it  --name m.menschikov.agent_api_cntrn --memory=32g --memory-swap=32g --cpuset-cpus=0-4 --gpus '"device=1"' m.menschikov/agent_api:v2

##### Команды для генерации документации:
* find . -type d -name __pycache__ -exec rm -r {} \+
* sphinx-apidoc -o ../docs/tmp/ .
* make html
* make latexpdf
* make singlehtml
* make clean

##### Команды для тестироваания
* pytest --cov=src --cov-report=html ...
* pygount src/ --suffix=py --format=summary

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
