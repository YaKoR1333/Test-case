recommendation_dialog_tree = {
    'hello': ['hello_null', 'hello_repeat', 'hangup_null', 'recommend_main', 'hangup_wrong_time'],
    'hello_repeat': ['hello_null', 'hangup_null', 'recommend_main', 'hangup_wrong_time'],
    'hello_null': ['hello_repeat', 'hello_null', 'recommend_main', 'hangup_wrong_time'],
    'recommend_main': ['hangup_null', 'recommend_null', 'recommend_default', 'hangup_negative',
                       'hangup_positive', 'recommend_score_negative', 'recommend_score_neutral',
                       'recommend_score_positive', 'recommend_repeat', 'recommend_repeat_2',
                       'hangup_wrong_time', 'forward'],
    'recommend_repeat': ['hangup_null', 'recommend_null', 'recommend_default', 'hangup_negative',
                         'hangup_positive', 'recommend_score_negative', 'recommend_score_neutral',
                         'recommend_score_positive', 'recommend_repeat_2',
                         'hangup_wrong_time', 'forward'],
    'recommend_repeat_2': ['hangup_null', 'recommend_null', 'recommend_default', 'hangup_negative',
                           'hangup_positive', 'recommend_score_negative', 'recommend_score_neutral',
                           'recommend_score_positive', 'recommend_repeat', 'hangup_wrong_time', 'forward'],
    'recommend_score_negative': ['hangup_null', 'recommend_null', 'recommend_default', 'hangup_negative',
                                 'hangup_positive', 'recommend_repeat', 'recommend_repeat_2',
                                 'hangup_wrong_time', 'forward'],
    'recommend_score_neutral': ['hangup_null', 'recommend_null', 'recommend_default', 'hangup_negative',
                                'hangup_positive', 'recommend_repeat', 'recommend_repeat_2',
                                'hangup_wrong_time', 'forward'],
    'recommend_score_positive': ['hangup_null', 'recommend_null', 'recommend_default', 'hangup_negative',
                                 'hangup_positive', 'recommend_repeat', 'recommend_repeat_2',
                                 'hangup_wrong_time', 'forward'],
    'recommend_null': ['hangup_null', 'recommend_default', 'hangup_negative',
                       'hangup_positive', 'recommend_score_negative', 'recommend_score_neutral',
                       'recommend_score_positive', 'recommend_repeat', 'recommend_repeat_2',
                       'hangup_wrong_time', 'forward'],
    'recommend_default': ['hangup_null', 'hangup_negative', 'hangup_positive', 'recommend_score_negative',
                          'recommend_score_neutral', 'recommend_score_positive', 'recommend_repeat',
                          'recommend_repeat_2', 'hangup_wrong_time', 'forward'],
    'hangup_positive': '',
    'hangup_negative': '',
    'hangup_wrong_time': '',
    'hangup_null': '',
    'forward': '',
}