import NeuroNetLibrary
import NeuroVoiceLibrary
import NeuroNluLibrary

import queue

import dialog_tree
import dialog_answers

nn = NeuroNetLibrary(nlu_call, event_loop)
nlu = NeuroNluLibrary(nlu_call, event_loop)
nv = NeuroVoiceLibrary(nlu_call, loop)

q = queue.Queue()
beg_dialog = 'hello'

q.put(beg_dialog)
visited_branch = set()

nv.media_params({'asr': 'google', 'tts': 'google', 'lang': 'ru_RU'})


def hello_logic_entity_list() -> list[str]:
    """возвращает список сущностей для распознавания в hello_logic"""

    return ['confirm', 'wrong_time', 'repeat']


def main_logic_entity_list() -> list[str]:
    """возвращает список сущностей для распознавания в main_logic"""

    return ['recommendation_score', 'recommendation', 'question', 'wrong_time', 'repeat']


def _clear_queue():
    """отчищает очередь"""

    while not q.empty():
        q.get()


def _add_node_in_queue(node: str):
    """добавляет новые диалоговые узлы и добавляет посещённый узел в множество, предварительно очищает очередь"""

    _clear_queue()
    visited_branch.add(node)
    for node in dialog_tree.recommendation_dialog_tree[node]:
        q.put(node)


def _check_recommend_main_in_visited_branch() -> bool:
    """проверяет посещение диалогового узла recommend_main"""

    return 'recommend_main' in visited_branch


def _check_len_visited_branch() -> bool:
    """проверка на то, что ни один диалоговый узел не был посещён"""

    return len(visited_branch) == 0


def _check_len_message(data: str) -> bool:
    """проверка на то сказано ли хоть что-то"""

    return len(data) > 0


def _check_dialog_has_record(prompt_lit: list[str]):
    """проверяет существования аудио файлов для диалога, если файла нет дозаливаем его"""
    for prompt in prompt_lit:
        if nv.has_record(prompt) is False:
            pass


def _dialog_node(node: str, next_logic_step: str):
    """вызывает проигрывание аудио файла промпта и добавляет возможные узлы в очередь"""

    recommend_null_count = nn.counter('recommend_null_count')
    hello_null_count = nn.counter('hello_null_count')
    recommend_default_count = nn.counter('recommend_default_count')

    if node == 'hello_null':
        hello_null_count = nn.counter('recommend_null_count', '+')
    elif node == 'recommend_default':
        recommend_default_count = nn.counter('recommend_default_count', '+')
    elif node == 'recommend_null':
        recommend_null_count = nn.counter('recommend_null_count', '+')

    if recommend_null_count == 2 or recommend_default_count == 2 or hello_null_count == 2:
        _dialog_end('hangup_null', 'dialogue_outcome')
    else:
        nv.say(node)
        _add_node_in_queue(node)

    return exec(next_logic_step + '()')


def _dialog_end(node: str, dialog_outcome: str):
    """вызывает проигрывание аудио файла промпта и завершает диалог"""

    nv.say(node)
    _dialog_done(node, dialog_outcome)


def _dialog_done(node: str, dialog_outcome: str):
    """заносит результат диалога в логи, отчищает очередь и завершает диалог"""

    nn.log(dialog_outcome, dialog_answers.dialog_answers(node)[1])
    _clear_queue()
    nn.dialog.result = nn.RESULT_DONE


def _recognizer(data: str, r, next_logic_step: str):
    """определяет какой должен быть ответ от робота"""

    while q.qsize() > 0:

        get_node = q.get()

        check_list = (r.result.entity('confirm'), r.result.entity('wrong_time'), r.result.entity('repeat'),
                      tuple(r.result.entity('recommendation_score')), r.result.entity('recommendation'),
                      r.result.entity('question'), get_node, _check_len_message(data), _check_len_visited_branch(),
                      _check_recommend_main_in_visited_branch())
        check_dict = {
            (None, None, None, None, None, None, 'hello', False, True, False): _dialog_node,
            (None, None, None, None, None, None, 'hello_null', False, False, False): _dialog_node,
            (None, None, True, None, None, None, 'hello_repeat', True, False, False): _dialog_node,
            (True, None, None, None, None, None, 'recommend_main', True, False, False): _dialog_node,
            (None, None, None, None, None, None, 'recommend_main', True, False, False): _dialog_node,
            (None, None, None, None, None, None, 'recommend_null', False, False, True): _dialog_node,
            (None, None, None, None, 'negative', None, 'recommend_score_negative', True, False, True): _dialog_node,
            (None, None, None, None, 'neutral', None, 'recommend_score_neutral', True, False, True): _dialog_node,
            (None, None, None, None, 'positive', None, 'recommend_score_positive', True, False, True): _dialog_node,
            (None, None, True, None, None, None, 'recommend_repeat', True, False, True): _dialog_node,
            (None, None, None, None, 'dont_know', None, 'recommend_repeat_2', True, False, True): _dialog_node,
            (None, None, None, None, None, None, 'recommend_default', True, False, True): _dialog_node,
            (None, True, None, None, None, None, 'hangup_wrong_time', True, False, True | False): _dialog_end,
            (None, None, None, tuple(range(9)), None, None, 'hangup_negative', True, False, True): _dialog_end,
            (None, None, None, tuple(range(9, 11)), None, None, 'hangup_positive', True, False, True): _dialog_end,
            (None, None, None, None, None, True, 'forward', True, False, True): _dialog_end,
        }
        if check_list in check_dict:
            return check_dict[check_list](get_node, next_logic_step)
        else:
            continue

    else:
        raise InvalidCallStateError(nn.log("Call ended"))


def hello_main():
    nn.log('unit', 'hello_main')
    with nv.listen(entities=hello_logic_entity_list()) as r:
        data = r.result.utterance()
        _recognizer(data, r, 'hello_logic')


def hello_logic():
    with nv.listen(entities=hello_logic_entity_list()) as r:
        data = r.result.utterance()
        if r.result.entity('confirm') or (r.result.has_entities() is False and data):
            _recognizer(data, r, 'main_logic')
        elif (r.result.entity('confirm') is False) or r.result.entity('wrong_time'):
            _recognizer(data, r, 'dialogue_outcome')
        else:
            _recognizer(data, r, 'hello_logic')


def main_logic():
    with nv.listen(entities=main_logic_entity_list()) as r:
        data = r.result.utterance()
        if r.result.has_entity('recommendation_score')\
                or r.result.entity('wrong_time')\
                or r.result.entity('question'):
            _recognizer(data, r, 'dialogue_outcome')
        else:
            _recognizer(data, r, 'main_logic')


def main():
    _check_dialog_has_record(dialog_tree.recommendation_dialog_tree.keys())
    try:
        hello_main()
    except InvalidCallStateError:
        nn.log("Call ended")


if __name__ == '__main__':
    main()
