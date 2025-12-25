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
Кроме того, потребуется сымитировать работу python скрипта `get_dc_envfile.py` (о нем будет рассказано ниже). Для этого нужно поместить конфиг файлы, связанные с графом (kgconn_params.yaml, kgenv_params.yaml, kghyperp_params.yaml) в директорию `/experiments/qa/init_env/env_settings/<DATASET_NAME>/<KNOWLEDGE_GRAPH_NAME>/`.

Чтобы избежать непредвиденных проблем рекомендуется поднять новый контейнер с привязкой к уже построенному графу, используя обновленный .env файл.

#### Предусловия
1. Граф знаний уже построен и лежит в каталоге вида: `data/knowledge_graphs/<DATASET_NAME>/<KNOWLEDGE_GRAPH_NAME>/`
2. Внутри директории графа должны существовать файлы настроек:
    ```
    /data/knowledge_graphs/<DATASET_NAME>/<KNOWLEDGE_GRAPH_NAME>/settings/kgenv_params.yaml
    /data/knowledge_graphs/<DATASET_NAME>/<KNOWLEDGE_GRAPH_NAME>/settings/kgconn_params.yaml
    /data/knowledge_graphs/<DATASET_NAME>/<KNOWLEDGE_GRAPH_NAME>/settings/kghyperp_params.yaml
    ```
3. QA-вопросы находятся на хосте по пути: `<REPO_ROOT>/data/qa_datasets//<DATASET_NAME>/qa_pairs.csv`

#### Docker-образ `workspace`
Соберите образ при помощи команды:
```
docker build -f deployment/workspace.Dockerfile -t workspace:v5 .
```
#### Настройка `qaenv_params.yaml`
Отредактируйте файл `/experiments/qa/init_env/qaenv_params.yaml`. Укажите как минимум следующие параметры:
 - DATASET_NAME
 - KNOWLEDGE_GRAPH_NAME
 - BASE_PERSONALAI_PATH — абсолютный путь до корня репозитория
 - BASE_KG_PATH — абсолютный путь на хосте до корня knowledge_graphs (путь, где лежат ваши графы - благодаря этой привязке они и окажутся в созданном контейнере)
 - Примечание:  если на вашей машине нет GPU, можно оставить `GPUS_CONFIG` как есть, но позже потребуется закомментировать определенные строки в docker-compose файле (см. ниже)
#### Генерация env-файла `.qaexp_env`
Docker Compose использует env-файл, сгенерированный скриптом `/experiments/qa/init_env/get_dc_envfile.py`. Результат его работы записывается в `/experiments/qa/init_env/env_settings/<DATASET_NAME>/<KNOWLEDGE_GRAPH_NAME>/.qaexp_env`. Выполните этот python скрипт, чтобы получить файл с зависимостями .env, необходимый для дальнейшего запуска контейнеров. В качестве аргумента при запуске python скрипта укажите путь до `qaenv_params.yaml`.
#### Запуск контейнеров
Перейдите в директорию `/experiments/qa/init_env` и с помощью docker-compose файла и сгенерированного на предыдущем этапе `.qaexp_env` файла поднимите контейнеры:
```
docker-compose --env-file="env_settings/<DATASET_NAME>/<KNOWLEDGE_GRAPH_NAME>/.qaexp_env" up -d mongo_ui redis_ui ollama_agent neo4j mongo_cache redis_cache qdrant opensearch workspace.
```
 - Примечание:  если на вашей машине нет GPU, закомментируйте в docker-compose файле строчки, требующие использование видеокарты:
    ```
    # devices:
    #   - driver: nvidia
    #     device_ids: ['${WORKSPACE_DEVICE_ID}']
    #     capabilities: [gpu]
    ```


### Запуск QA-эксперимента
После старта окружения запустите пайплайн генерации ответов и оценки качества. Удобнее всего использовать готовые shell-скрипты.

#### Вариант A: запуск одного эксперимента (run_experiment.sh)
1. Подключитесь к созданному workspace-контейнеру через интерактивную консоль. Пример команды:
    ```
    docker exec -it -u root <ID контейнера> bash
    ```
2. Запустите эксперимент с помощью скрипта `run_experiment.sh`. Этот скрипт инициализирует структуру директорий эксперимента, запустит генерацию ответов и оценку их качества, а также сохранит логи в директории эксперимента. Пример команды:
    ```
    cd /home/workspace/experiments/qa
    bash run_experiment.sh <KG_NAME> <DATASET_NAME> <EXP_NAME> \
        <path/to/qahyperp_params.yaml> <path/to/expdir_params.yaml> <path/to/eval_params.yaml>
    ```
    где:
     - `<KG_NAME>` - имя графа знаний
     - `<DATASET_NAME>` - имя датасета
     - `<EXP_NAME>` - имя эксперимента
     - `<path/to/... .yaml>` - путь к соответствующему конфигу. Важно указывать именно абсолютный путь!

    Примечания:
     - Если для установки зависимостей в контейнере вы создавали отдельное виртуальное окружение, то в .sh скриптах, которые задействуются скриптом `run_experiment.sh` (и в нем самом) нужно заменить `PYTHON_CMD=/usr/bin/python3` на `PYTHON_CMD=/opt/venv/bin/python` (замените в `/configure/init_exp_environment.sh`, `/generate/generate.sh`, `/evaluate/evaluate.sh`, `run_experiment.sh`).
     - По аналогии с тем, как это было в kg_building в модуль `/experiments/qa/generate/generate_answers.py` нужно добавить функцию для вашего датасета с вопросами, полагаясь на уже реализованные функции. Эта функция должна читать `qa_pairs.csv` и возвращать списоки вопросов и ответов в нужном формате. Вставьте её в словарь `CUSTOM_LOAD_FUNCS` под ключом, совпадающим с именем вашего датасета (переменная `DATASET_NAME` в `kghyperp_params.yaml`).
     - В рамках QA пайплайна используется та же конфигурация LLM агента, что была задана в файле `kghyperp_params.yaml` при построении графа знаний.

#### Вариант B: запуск группы экспериментов
Если нужно прогнать несколько конфигураций, используйте `run_all_experiments.sh` или `run_grouped_by_graph_exps.sh`.
#### 1) `run_all_experiments.sh`: несколько экспериментов для одного графа
Предназначен для последовательного прогона нескольких экспериментов (с разными гиперпараметрами). Для запуска в `experiments/qa/params_to_run/` должны быть подготовлены yaml-файлы. Также в `experiments/qa/configure/prepared_params/` должны существовать базовые expdir- и eval-конфиги.

`run_all_experiments.sh` вызывается либо через `crontab_job.sh` (см. ниже), либо напрямую в контейнере `workspace`. Пример команды для запуска внутри контейнера:
```bash
cd /home/workspace/experiments/qa
bash run_all_experiments.sh <KNOWLEDGE_GRAPH_NAME> <DATASET_NAME> <EXPDIR_CINFIG_FNAME> <EVAL_CONFIG_FNAME>
```
Скрипт пройдёт по всем файлам в `params_to_run` и выполнит `run_experiment.sh` для каждого. Лог запишется в `runexperiment_log.txt`.
#### 2) `run_grouped_by_graph_exps.sh`: несколько датасетов/графов (групповой прогон)
Предназначен для прогона экспериментов сразу по нескольким `<DATASET_NAME, KNOWLEDGE_GRAPH_NAME>`. Для запуска для каждого `<DATASET_NAME, KNOWLEDGE_GRAPH_NAME>` должны существовать подготовленные yaml конфиги гиперпараметров экспериментов по пути: `/experiments/qa/configure/medium/prepared_params/<DATASET_NAME>/<KNOWLEDGE_GRAPH_NAME>/
`. Эти файлы будут скопированы в `params_to_run/` и именно они определяют, какие эксперименты будут запущены.

Скрипт делает следующее:
1. Поднимает временный workspace контейнер (из deployment). Редактирует qaenv_params-файл, затем останавливает и удаляет временный контейнер. После запускает `prepare_env_files.sh`, который создаёт .qaexp_env файл.
2. Поднимает окружение для проведения QA-экспериментов по конкретному графу знаний.
3. Подготавливает пакет экспериментов: Чистит `/experiments/qa/params_to_run/` и копирует туда файлы из `prepared_params`.
4. Запускает эксперименты: вызывает `crontab_job.sh` внутри контейнера, что приводит к запуску `run_all_experiments.sh` и записи лога в `crontab_log.txt`.
5. Очищает окружение: останавливает и удаляет контейнеры окружения для текущей пары `<DATASET_NAME, KNOWLEDGE_GRAPH_NAME>` через `rm_containers.sh`.

На выходе получаем набор результатов по каждому эксперименту в директории: `/experiments/qa/results/<DATASET_NAME>/<KNOWLEDGE_GRAPH_NAME>/<EXP_NAME>/`.

#### Cron для запуска qa-экспериментов
Про непосредственный запуск экспериментов было рассказано выше. Кроме того, можно осуществить непосредственный запуск и при помощи `crontab_job.sh` - обертки, запускающей `run_all_experiments.sh`. Именно через неё и осуществляется запуск экспериментов в `run_grouped_by_graph_exps.sh`.

Вы можете добавить задачу на запуск экспериментов в планировщик cron внутри контейнера, вместо ручного запуска. Для этого скопируйте шаблон задания (из `run_crontab.txt`) в crontab контейнера. Например, чтобы поставить запуск задачи каждый день в 4 часа утра 0 минут, можно в контейнере выполнить crontab -e и добавить строку:
```
0 4 * * * bash /home/workspace/experiments/qa/run_grouped_by_graph_exps.sh >> /home/workspace/experiments/qa/grouped_run_crontab.txt 2>&1
```

### Просмотр результатов
Результаты сохраняются в смонтированную директорию `experiments/qa/results`.
 - **Сгенерированные ответы:** JSON-файлы сохраняются в `results/<DATASET_NAME>/<KG_NAME>/<EXP_NAME>/answer_packs/`. Формат:
    ```
    {
      "0": {
        "question": "Кем хочет стать пользователь?",
        "gold_answer": "Полицейским",
        "gen_answer": "Пользователь хочет стать полицейским."
      },
    }
    ```
 - **Метрики качества:** файлы метрик лежат в `metric_packs/` (базовые метрики) и `judges_packs/` (метрики LLM-as-a-Judge). Итоговая агрегация сохраняется в `accumulated_scores.json`:
    ```
    {
      "BLEU1": 0.45,
      "BLEU2": 0.30,
      "METEOR": 0.50,
      "RougeL": 0.52,
      "ExactMatch": 0.40,
      "NoneScore": 0.00,
      "NoAnswerScore": 0.0,
      "llm-as-a-judge_mean": 0.73,
      "llm-as-a-judge_median": 0.75,
      "elapsed_time": 123.45
    }
    ```
     - Примечание: LLM-as-a-Judge (если включен) требует доступности Judge-модели (по умолчанию Qwen-7B через Ollama). Если вам не требуется оценка с помощью LLM можете закомментировать вызов скрипта `evaluate_llmjudge.py` в `/evaluate/evaluate.sh`.
 - **Логи:** записываются в `accumulatescores_log.txt`, `inference_log.txt`, `baseeval_log.txt`, `llmasajudgeeval_log.txt` в директории эксперимента.

Следуя шагам выше, вы сможете запустить QA-пайплайн и получить JSON-ответы и метрики качества.