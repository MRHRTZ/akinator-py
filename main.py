import inquirer

from akinator import Akinator


def show_question(akinator, session_data):
    max_progression = 90.0
    question = session_data['question']
    answers = session_data['answers']
    answers = list(map(lambda x: x['answer'], answers))
    step = session_data['step']
    progression = float(session_data['progression'])

    if progression > max_progression:
        # WIN
        win_data = akinator.end_question()
        name = win_data['name']
        desc = win_data['description']
        image = win_data['absolute_picture_path']
        print('='*40)
        print(name)
        print(desc)
        print('image :', image)
        return True, None
    else:
        # STILL QUESTION
        questions_prompt = [
            inquirer.List(
                "answer",
                message=f"[{int(step)+1}] {question}",
                choices=answers,
            ),
        ]
        answer = inquirer.prompt(questions_prompt)['answer']
        session_data = akinator.answer_question(answers.index(answer))

        return False, session_data


akinator = Akinator()
regions = akinator.show_regions()

print('Welcome to akinator~!')
questions = [
    inquirer.List(
        "region",
        message="Select your region",
        choices=regions.keys(),
    ),
]

answers = inquirer.prompt(questions)
akinator.select_region(answers['region'])
akinator.create_new_session()

question = akinator.show_question()

win = False
while not win:
    win, question = show_question(akinator, question)