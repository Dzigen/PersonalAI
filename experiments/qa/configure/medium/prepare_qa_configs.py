
elif PARAMS['BASE_KGR_CONFIG']['name'] == 'medium':

    if PARAMS['MEDIUM_KG_REASONER']['knowledge_retriever_config']['filter_method'] == 'None':
        filter_method = None
        filter_config = None
    else:
        filter_method = PARAMS['MEDIUM_KG_REASONER']['knowledge_retriever_config']['filter_method']
        filter_config = PARAMS['MEDIUM_KG_REASONER']['knowledge_retriever_config']['filter_config']

    k_retriever_config = KnowledgeRetrieverConfig(
        retriever_method=PARAMS['MEDIUM_KG_REASONER']['knowledge_retriever_config']['retriever_method'],
        retriever_config=PARAMS['MEDIUM_KG_REASONER']['knowledge_retriever_config']['retriever_config'],
        filter_method=filter_method, filter_config=filter_config)

    kg_reasoner_config = MediumKGReasonerConfig(
        searchplan_enhancer_config=SearchPlanEnhancerConfig(
            lang=PARAMS['BASE_KGR_CONFIG']['lang'], adriver_config=adriver_config,
            plan_initing_agent_task_config=AgentPlanInitTaskConfigSelector.select(
                base_config_version=PARAMS['MEDIUM_KG_REASONER']['searchplan_enhancer_config']['plan_initing_agent_task_version']
            ),
            enhance_classifier_agent_task_config=AgentEnhanceClassifierTaskConfigSelector.select(
                base_config_version=PARAMS['MEDIUM_KG_REASONER'][
                    'searchplan_enhancer_config']['enhance_classifier_agent_task_version']
            ),
            plan_enhancing_agent_task_config=AgentPlanEnhancingTaskConfigSelector.select(
                base_config_version=PARAMS['MEDIUM_KG_REASONER']['searchplan_enhancer_config']['plan_enhancing_agent_task_version']
            )
        ),
        entities_extractor_config=EntitiesExtractorConfig(
            lang=PARAMS['BASE_KGR_CONFIG']['lang'], adriver_config=adriver_config,
            entities_extraction_agent_task_config=AgentEntitiesExtrTaskConfigSelector.select(
                base_config_version=PARAMS['MEDIUM_KG_REASONER'][
                    'entities_extractor_config']['entities_extraction_agent_task_version']
            )
        ),
        e2n_matcher_config=Entities2NodesMatcherConfig(
            use_tree=PARAMS['MEDIUM_KG_REASONER']['e2n_matcher_config']['use_tree'],
            distance_threshold=PARAMS['MEDIUM_KG_REASONER']['e2n_matcher_config']['distance_threshold'],
            max_n=PARAMS['MEDIUM_KG_REASONER']['e2n_matcher_config']['max_n'],
            fetch_k=PARAMS['MEDIUM_KG_REASONER']['e2n_matcher_config']['fetch_k']
        ),
        cluequeries_generator_config=ClueQueriesGeneratorConfig(
            lang=PARAMS['BASE_KGR_CONFIG']['lang'], adriver_config=adriver_config,
            cquerie_generator_agent_task_config=AgentCQueryGenTaskConfigSelector.select(
                base_config_version=PARAMS['MEDIUM_KG_REASONER'][
                    'cluequeries_generator_config']['cquerie_generator_agent_task_version']
            )
        ),
        knowledge_retriever_config=k_retriever_config,
        clueanswer_generator_config=ClueAnswerGeneratorConfig(
            lang=PARAMS['BASE_KGR_CONFIG']['lang'], adriver_config=adriver_config,
            cagen_agent_task_config=AgentClueAnswerGenTaskConfigSelector.select(
                base_config_version=PARAMS['MEDIUM_KG_REASONER'][
                    'clueanswer_generator_config']['canswer_generator_agent_task_version']
            )
        ),
        clueanswers_summarizer_confif=ClueAnswersSummarizerConfig(
            lang=PARAMS['BASE_KGR_CONFIG']['lang'], adriver_config=adriver_config,
            canswers_summarisation_agent_task_config=AgentClueAnswersSummTaskConfigSelector.select(
                base_config_version=PARAMS['MEDIUM_KG_REASONER'][
                    'clueanswers_summarizer_confif']['canswers_summarisation_agent_task_version']
            )
        ),
        answer_generator_config=AnswerGeneratorConfig(
            lang=PARAMS['BASE_KGR_CONFIG']['lang'], adriver_config=adriver_config,
            answer_classifier_agent_task_config=AgentAnswerClassifierTaskConfigSelector.select(
                base_config_version=PARAMS['MEDIUM_KG_REASONER']['answer_generator_config']['answer_classifier_agent_task_version']
            ),
            answer_generator_agent_task_config=AgentAnswerGeneratorTaskConfigSelector.select(
                base_config_version=PARAMS['MEDIUM_KG_REASONER']['answer_generator_config']['answer_generator_agent_task_version']
            )
        ),
        max_searchplan_steps=PARAMS['MEDIUM_KG_REASONER']['max_searchplan_steps']
    )
else:
    raise ValueError