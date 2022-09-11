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


def _check_recommend_main_in_visited_branch():
    """проверяет посещение диалогового узла recommend_main"""

    return 'recommend_main' in visited_branch


def _check_len_visited_branch():
    """проверка на то, что ни один диалоговый узел не был посещён"""

    return len(visited_branch) == 0


def _check_len_message(data: str):
    """проверка на то сказано ли хоть что-то"""

    return len(data) > 0


def _dialog_node(node: str):
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
        _dialog_end('hangup_null')
    else:
        if nv.has_record(node):
            nv.say(node)
            _add_node_in_queue(node)
        else:
            nv.synthesize(dialog_answers.dialog_answers(node))
            _add_node_in_queue(node)

    return main()


def _dialog_end(node: str):
    """вызывает проигрывание аудио файла промпта и завершает диалог"""

    if nv.has_record(node):
        nv.say(node)
        _dialog_done(node)
    else:
        nv.synthesize(dialog_answers.dialog_answers(node)[0])
        _dialog_done(node)


def _dialog_done(node: str):
    """заносит результат диалога в логи, отчищает очередь и завершает диалог"""

    nn.log('dialogue_outcome', dialog_answers.dialog_answers(node)[1])
    _clear_queue()
    nn.dialog.result = nn.RESULT_DONE


def main():

    with nv.listen(entities='confirm, wrong_time, repeat, recommendation_score, recommendation, question') as r:

        nv.media_params({'asr': 'google', 'tts': 'google', 'lang': 'ru_RU'})

        while True:
            get_node = q.get()
            data = r.result.utterance()
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
                exec(check_dict[check_list](get_node))
            else:
                continue


if __name__ == '__main__':
    main()
