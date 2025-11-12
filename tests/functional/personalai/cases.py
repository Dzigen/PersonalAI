import sys
# TO CHANGE
PROJECT_BASE_DIR = '../'
TEST_VOLUME_DIR = './volumes'
sys.path.insert(0, PROJECT_BASE_DIR)

RAW_TEXTS_RU = [
    "Проживающие в общежитии студенты имеют право rруглосуточного доступа к месту проживания.",
    "Проживающие в общежитии студенты имеют право обратиться к администрации ФГБУ «МСГ» с заявлением, заверенным заведующим общежития, о размещении в гостевых комнатах общежития родственников (на короткий период пребывания, не менее 2-х суток), родителей - на любой срок (при предоставлении документа, подтверждающего степень родства).",
    "Проживающие в общежитии студенты имеют право пользоваться помещениями для самостоятельных занятий и помещениями культурно-бытового назначения, оборудованием, инвентарем общежития.",
    "Проживающие в общежитии студенты имеют право обращаться к администрации корпуса с просьбами о своевременном ремонте, замене оборудования и инвентаря, вышедшего из строя не по их вине.",
    "Проживающие в общежитии студенты имеют право на переселение из одного помещения в другое в том же корпусе, а также на переселение из одного корпуса в другой при наличии свободных мест, с согласия администрации корпуса.",
    "Проживающие в общежитии студенты имеют право участвовать в формировании и выборах Студенческого совета МСГ и быть избранным в его состав.",
    "Проживающие в общежитии студенты имеют право участвовать (вносить предложения) через Студенческий совет МСГ и отдел по молодежной политике ФГБУ «МСГ» в решении вопросов совершенствования жилищно-бытовых условий, организации воспитательной работы и досуга.",
    "Проживающие в общежитии студенты имеют право принимать участие в общественных, спортивных и культурно-досуговых мероприятиях, организованных администрацией ФГБУ «МСГ» и Студенческим советом МСГ.",
    "Проживающие в общежитии студенты имеют право пользоваться разрешенной бытовой техникой с соблюдением правил техники безопасности и правил пожарной безопасности.",
    "Проживающие в общежитии студенты имеют право бесплатно посещать Межвузовский  учебно-спортивный центр в утвержденное администрацией ФГБУ «МСГ» и согласованное со Студенческим советом МСГ время.",
    "Проживающие в общежитии студенты имеют право бесплатно посещать душевой комплекс с сауной ФГБУ «МСГ» в отведенное администрацией ФГБУ «МСГ» время.",
]

RAW_TEXTS_EN = [
    "Students living in the dormitory have the right to 24-hour access to their place of residence.",
    "Students living in the dormitory have the right to apply to the administration of the Federal State Budgetary Institution 'MSG' with an application, certified by the head of the dormitory, for the placement of relatives in the guest rooms of the dormitory (for a short period of stay, at least 2 days), parents - for any period (upon presentation of a document confirming the degree of kinship).",
    "Students living in the dormitory have the right to use the rooms for independent study and cultural and household premises, equipment, inventory of the dormitory.",
    "Students living in the dormitory have the right to contact the administration of the building with requests for timely repairs, replacement of equipment and inventory that failed through no fault of theirs.",
    "Students living in the dormitory have the right to move from one room to another in the same building, as well as to move from one building to another if there are vacancies, with the consent of the administration buildings.",
    "Students living in the dormitory have the right to participate in the formation and election of the MSG Student Council and to be elected to its composition.",
    "Students living in the dormitory have the right to participate (make proposals) through the MSG Student Council and the youth policy department of the FSBI 'MSG' in resolving issues of improving housing and living conditions, organizing educational work and leisure.",
    "Students living in the dormitory have the right to take part in social, sports and cultural and leisure events organized by the administration of the FSBI 'MSG' and the MSG Student Council.",
    "Students living in the dormitory have the right to use permitted household appliances in compliance with safety regulations and fire safety regulations.",
    "Students living in the dormitory have the right to visit the Interuniversity Educational and Sports Center free of charge at a time approved by the administration of the FSBI 'MSG' and agreed upon with the MSG Student Council."
]

QUESTIONS = {
    'ru': [
        "Какими помещениями разрешено пользоваться студентам, проживающем в общещитии МСГ?",
        "Разрешено ли студентами, проживающим в общежитии МСГ пользоваться бытовой техникой?",
        "Могут ли проживающие в общежитии МСГ ображаться к администрации с вопросами?"
    ],
    'en': [
        "What facilities are students allowed to use while living in the MSG dormitory?",
        "Are students living in the MSG dormitory allowed to use household appliances?",
        "Can residents of the MSG dormitory contact the administration with questions?"
    ]
}

POPULATED_QUERIES_TEST_CASES = []
for language, questions in QUESTIONS.items():
    for question in questions:
        POPULATED_QUERIES_TEST_CASES.append([question, language])
