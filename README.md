### ✨ About
---

#### Материалы
- [Отчёт 2025](docs/source/_static/iteration_summary/2025/PersonalAI(Отчёт)(НИР)(Skoltech-Sber)(2025).pdf)
- [Презентация работ 2025](docs/source/_static/iteration_summary/2025/PersonalAI(ПриёмкаРабот)(НИР)(Skoltech-Sber)(2025).pdf)

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

### 🚀 Quick Start
---
TODO

### 📊 Benchmarks
---
TODO

### 📚 Documentation
---
TODO

### 🛠️ Utils
---

#### Полезные материалы
* [MLOps](docs/source/_static/useful_material/MLOps/)
* [Организация научных исследований](docs/source/_static/useful_material/ОрганизацияНаучныхИсследований/)

#### Команды для генерации документации:
* find . -type d -name __pycache__ -exec rm -r {} \+
* sphinx-apidoc -o ../docs/tmp/ .
* make html
* make latexpdf
* make singlehtml
* make clean

#### Генерация диаграммы классов
* pyreverse -o puml -f ALL src/

#### Команды для тестироваания
* pytest --cov=src --cov-report=html ...
* pygount src/ --suffix=py --format=summary

#### Команды для проверки стиля кодовой базы
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

utils:
* find . -maxdepth 4 -type d -name "tmp_*" -exec rm -rf {} +
* git tag -a <tag-version> commit_id -m "comment"

archive experiments:
* tar -czvf  deepseek_231025_v2prompts.tar.gz --exclude="configs" --exclude="judge_packs" --exclude="metric_packs" --exclude="tmp_answer_packs" --exclude="tmp_judges_packs" --exclude="inference_log.txt"  deepseek_231025_v2prompts/

### 🤝 Community and Contributing
---
TODO

### 📄 Citation
---
```
@article{11479299,
  author={Menschikov, Mikhail and Evseev, Dmitry and Dochkina, Victoria and Kostoev, Ruslan and Perepechkin, Ilia and Anokhin, Petr and Semenov, Nikita and Burnaev, Evgeny},
  journal={IEEE Access}, 
  title={PersonalAI: A Systematic Comparison of Knowledge Graph Storage and Retrieval Approaches for Personalized LLM Agents}, 
  year={2026},
  volume={14},
  number={},
  pages={58262-58281},
  keywords={Filtering;Filters;Circuits and systems;Communication systems;Computer networks;IP networks;Mobile handsets;Telecommunications;Large language models;Artificial intelligence;GraphRAG;graph traversal approaches;knowledge graphs generation;multiagency;question answering},
  doi={10.1109/ACCESS.2026.3682941}}
```
```
@misc{menschikov2026personalai20enhancingknowledge,
      title={PersonalAI 2.0: Enhancing knowledge graph traversal/retrieval with planning mechanism for Personalized LLM Agents}, 
      author={Mikhail Menschikov and Matvey Iskornev and Alexander Kharitonov and Alina Bogdanova and Mikhail Belkin and Ekaterina Lisitsyna and Artyom Sosedka and Victoria Dochkina and Ruslan Kostoev and Ilia Perepechkin and Evgeny Burnaev},
      year={2026},
      eprint={2605.13481},
      archivePrefix={arXiv},
      primaryClass={cs.CL},
      url={https://arxiv.org/abs/2605.13481}, 
}
```

### 🌟 Star, Cite, Collaborate
---
If this project inspires or assists you, please consider:
* ⭐ Starring the repository
* 🧵 Opening discussions or issues
* 📄 Citing the relevant paper(s)

Let’s build memory-aware LLM agents together!

### 📬 Technical Support
---
* [Telegram](https://t.me/mmenscshikov)
* [Mail](m.menschikov@skoltech.ru)
