import pynlpir


def analysis_text(text):
    text_dict = {}
    count_dict = {}
    text_count = {}
    pynlpir.open()
    res = pynlpir.segment(str(text).replace('\n','').replace(' ',''))
    for word in res:
        if word[0] not in text_count.keys():
            text_count[word[0]] = 1
        else:
            text_count[word[0]] += 1

        text_dict[word[0]] = word[1]

        if word[1] not in count_dict.keys():
            count_dict[word[1]] = 1
        else:
            count_dict[word[1]] += 1

    ana_res = {
        'count_dict' : count_dict,
        'text_dict' : text_dict,
        'text_count': text_count,
    }
    return ana_res


