## QA Pipeline - инструкция

### Обзор
Этот README описывает запуск QA-экспериментов (оценку качества QA-пайплайна), которые генерируют ответы с использованием построенного графа знаний и (опционально) оценивают качество ответов различными метриками. Следуя инструкции, вы получите JSON-файлы со сгенерированными ответами (минимальный результат) и, при необходимости, численную оценку качества (метрики вроде BLEU, METEOR и др.). Процесс включает подготовку конфигураций, запуск сервисов через Docker и выполнение скриптов QA-пайплайна.

**Предусловия:**
 - **Граф знаний** для вашего датасета уже построен (через пайплайн KG building). Вам понадобятся имя датасета и имя графа знаний из этого шага.
 - **QA-датасет** (вопросы и ответы) подготовлен. Обычно ожидается CSV-файл вида `/data/qa_datasets/<DATASET_NAME>/qa_pairs.csv` (колонки question и answer). Например, содержимое `qa_pairs.csv` может быть:
    ```
    question,answer,id
    "Кем хочет стать ... ?", "Полицейским",0
    "Сколько домашних животных есть у ... ?", "Двое",1
    ```
 - **Docker** подготовлен и настроен.

### Подготовка конфигурационных файлов
Перед запуском пайплайна убедитесь, что подготовлены (или скорректированы) следующие YAML-конфиги эксперимента:
1. **qahyperp_params.yaml (основные гиперпараметры QA пайплайна).** В зависимости от того, какой метод поиска собираетесь использовать (weak/medium), выберите соответствующий файл (`/experiments/qa/configure/weak/qahyperp_params.yaml` / `/experiments/qa/configure/medium/qahyperp_params.yaml`) и внесите в него изменения. Обновите имя эксперимента (`EXPERIMENT_NAME`), имя датасета (`DATASET_NAME`) и имя графа знаний (`KNOWLEDGE_GRAPH_NAME`) под ваш случай. При необходимости задайте гиперпараметры других стадий qa пайплайна: обработка запроса, reasoning, генерация ответа и так далее.
2. **expdir_params.yaml (директории эксперимента).** В этом файле (`/experiments/qa/configure/expdir_params.yaml`) задаются пути и имена файлов результатов. Обычно можно использовать без изменений, но нужно проверить корректность пути к QA-датасетам и секции `WORKSPACE_CONTAINER_DIRS`.
3. **eval_params.yaml (оценка качества ответов).** В файле (`/experiments/qa/evaluate/eval_params.yaml`) задаются основные параметры для оценки качества ответов системы. Здесь также задаются параметры агента для подсчета метрики LLM-as-a-Judge.
    - Примечание: если вам нужно вычислить метрики `precision`/`recall`,`f1` с помощью `BERTScore`, то перед запуском экспериментов убедитесь, что у вас загружена соответствующая модель (указанная в `eval_params.yaml` под `bertscore_model_path`). Для загрузки можете воспользоваться теми же скриптами из каталога `notebooks/download_models`, что использовались для загрузки эмбеддера при построении графа. Пример команды (исполняемой уже внутри контейнера):
        ```
        python electra.py
        ```
    Также убедитесь, что `lang` соответствует языку датасета.

### Сборка и запуск Docker-окружения
QA-пайплайн (как и memorize) зависит от нескольких сервисов (БД графа, векторных баз, кэшей и т. д.) и исполняющей среды, которые оркестрируются через Docker. В целом если вы уже прошли процесс построения графа и у вас уже поднято "KG-окружение", то можно не поднимать заново docker-контейнер. В этом случае можно запускать qa-эксперименты в имеющемся workspace. Однако нужно быть готовым к тому, что потребуется примонтировать некоторые директории, в частности необходимо примонтировать с хоста сам каталог `experiments`. Для этого добавьте соответствующую директорию в раздел `volumes` файла `kg_building/docker-compose.yaml` и пересоздайте workspace контейнер:
```
docker compose --env-file /data/knowledge_graphs/<dataset>/<graph>/.env -f kg_building/docker-compose.yaml up -d --force-recreate workspace
```
Чтобы избежать непредвиденных проблем 



Скрипты для оценки качества qa-конфигураций лежат в каталоге "experiments/qa_kg" (https://github.com/zer0o0ne/Personal-AI/tree/dev/experiments/qa_kg). Последовательность запуска скриптов следующая:
0. Указать конфигурацию эксперимента в params.yaml- (https://github.com/zer0o0ne/Personal-AI/blob/dev/experiments/qa_kg/params.yaml)файле.
1. Запустить init_file_structure.py (https://github.com/zer0o0ne/Personal-AI/blob/dev/experiments/qa_kg/init_file_structure.py) с указанием пути до полученного params.yaml (с шага 0). В результате будет инициализирована директория, куда будут сохраняться сгенерированные ответы + метрики.
2. Запустить prepare_qa_configs.py (https://github.com/zer0o0ne/Personal-AI/blob/dev/experiments/qa_kg/prepare_qa_configs.py) с указанием пути до полученного params.yaml (с шага 0). В результате будет создан/сохранён дамп QA-конфигурации (в dataclass-структуре) на основе указанных значений гиперпараметров в params.yaml-файле.
3. Поднять контейнеры с привязкой (mount) на соответствующую директорию с графом знаний.
3.1. Указать конфигурацию графа знаний в params.yam (https://github.com/zer0o0ne/Personal-AI/blob/dev/notebooks/kg_building/create/params.yaml)l-файле из каталога "notebooks/kg_building/create".
3.2. Запустить get_dc_envfile.py (https://github.com/zer0o0ne/Personal-AI/blob/dev/notebooks/kg_building/create/get_dc_envfile.py) с указанием пути до полученного params.yaml (с шага 3.1). В результате будет получен файл с зависимостями ".env_*" для запуска контейнеров.
3.3. С помощью docker-compose (https://github.com/zer0o0ne/Personal-AI/blob/dev/notebooks/kg_building/docker-compose.yaml)-файла в "notebooks/kg_building/"-каталоге и ".env_*"-файла (с шага 3.2), который лежит в корне каталога с соответствующим графом поднять контейнеры: docker-compose --env-file="путь до .env" up mongo_ui redis_ui ollama_agent neo4j.
4. Запустить generate_answers.py (https://github.com/zer0o0ne/Personal-AI/blob/dev/experiments/qa_kg/generate_answers.py) с указанием пути до полученного params.yaml (с шага 0). Будет запущен QA-пайплайн на указанном датасете. В результате будут получены/cохранены json-файлы с сгенерированными ответами.
5. Запустить evaluate_answers.py (https://github.com/zer0o0ne/Personal-AI/blob/dev/experiments/qa_kg/evaluate_answers.py) с указанием пути до полученного params.yaml (с шага 0). Будет выполнена оценка качества сгенерированных ответов с помощью следующих метрик: BLEU1, BLEU2, METEOR, RougeL, ExactMatch, BertScore, NoneScore. В результате будут получены/сохранены json-файлы со значениями метрик.
